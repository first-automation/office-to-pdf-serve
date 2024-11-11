import uno
from com.sun.star.beans import PropertyValue
from com.sun.star.table.CellContentType import EMPTY
from com.sun.star.table import CellRangeAddress
from com.sun.star.sheet import TablePageBreakData


class OfficeClient:
    def __init__(self, hostname: str | None = None, port: int | None = None) -> None:
        hostname = hostname or "localhost"
        port = port or 2002
        local_context = uno.getComponentContext()
        resolver = local_context.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local_context
        )
        context = resolver.resolve(
            f"uno:socket,host={hostname},port={port};urp;StarOffice.ComponentContext"
        )
        self.desktop = context.ServiceManager.createInstanceWithContext(
            "com.sun.star.frame.Desktop", context
        )
        self.document = None

    def load_document(self, input_url: str) -> None:
        self.document = self.desktop.loadComponentFromURL(input_url, "_blank", 0, ())

    def is_document(self) -> bool:
        return self.document.supportsService("com.sun.star.text.TextDocument")

    def is_sheet(self) -> bool:
        return self.document.supportsService("com.sun.star.sheet.SpreadsheetDocument")

    def is_range_blank(
        self, sheet, start_col: int, start_row: int, end_col: int, end_row: int
    ) -> bool:
        cell_range = sheet.getCellRangeByPosition(
            start_col, start_row, end_col, end_row
        )
        data_array = cell_range.getDataArray()
        for row in data_array:
            for cell_value in row:
                if cell_value != "":
                    return False
        return True

    def is_surround_blank(
        self,
        sheet,
        start_col: int,
        start_row: int,
        end_col: int,
        end_row: int,
        max_cols: int,
        max_rows: int,
    ) -> bool:
        inside_col_blank = self.is_range_blank(
            sheet, end_col, start_row, end_col, end_row
        )
        inside_row_blank = self.is_range_blank(
            sheet, start_col, end_row, end_col, end_row
        )
        outside_col_blank = True
        if end_col < max_cols:
            outside_col_blank = self.is_range_blank(
                sheet, end_col + 1, start_row, end_col + 1, end_row
            )
        outside_row_blank = True
        if end_row < max_rows:
            outside_row_blank = self.is_range_blank(
                sheet, start_col, end_row + 1, end_col, end_row + 1
            )
        return (inside_col_blank or outside_col_blank) and (
            inside_row_blank or outside_row_blank
        )

    def divide_print_areas(self, bounding_box, row_page_breaks, column_page_breaks):
        new_bounding_boxes = []
        manual_row_page_breaks = [
            row_page_break
            for row_page_break in row_page_breaks
            if row_page_break.ManualBreak
        ]
        manual_column_page_breaks = [
            column_page_break
            for column_page_break in column_page_breaks
            if column_page_break.ManualBreak
        ]
        if (
            not manual_row_page_breaks
            or manual_row_page_breaks[-1].Position < bounding_box.EndRow
        ):
            manual_row_page_breaks.append(TablePageBreakData(bounding_box.EndRow, True))
        if (
            not manual_column_page_breaks
            or manual_column_page_breaks[-1].Position < bounding_box.EndColumn
        ):
            manual_column_page_breaks.append(
                TablePageBreakData(bounding_box.EndColumn, True)
            )
        for i in range(len(manual_row_page_breaks)):
            for j in range(len(manual_column_page_breaks)):
                if i == 0:
                    row_page_break_start = bounding_box.StartRow
                else:
                    row_page_break_start = manual_row_page_breaks[i - 1].Position
                if j == 0:
                    column_page_break_start = bounding_box.StartColumn
                else:
                    column_page_break_start = manual_column_page_breaks[j - 1].Position
                row_page_break_end = manual_row_page_breaks[i].Position
                column_page_break_end = manual_column_page_breaks[j].Position
                new_bounding_boxes.append(
                    CellRangeAddress(
                        bounding_box.Sheet,
                        column_page_break_start,
                        row_page_break_start,
                        column_page_break_end,
                        row_page_break_end,
                    )
                )
        return new_bounding_boxes

    def update_print_areas(self) -> None:
        if not self.is_sheet():
            raise ValueError("This is not a sheet document")
        for sheet in self.document.Sheets:
            print_areas = sheet.getPrintAreas()
            if not print_areas:
                cell_cursor = sheet.createCursor()
                cell_cursor.gotoStartOfUsedArea(False)
                cell_cursor.gotoEndOfUsedArea(True)
                bounding_box = cell_cursor.getRangeAddress()
            else:
                bounding_box = print_areas[0]

            max_cols = sheet.Columns.Count - 1
            max_rows = sheet.Rows.Count - 1

            row_page_breaks = sheet.getRowPageBreaks()
            column_page_breaks = sheet.getColumnPageBreaks()
            bounding_boxes = self.divide_print_areas(
                bounding_box, row_page_breaks, column_page_breaks
            )

            if len(bounding_boxes) == 1:
                bounding_box = bounding_boxes[0]
                while True:
                    surround_blank = self.is_surround_blank(
                        sheet,
                        bounding_box.StartColumn,
                        bounding_box.StartRow,
                        bounding_box.EndColumn,
                        bounding_box.EndRow,
                        max_cols,
                        max_rows,
                    )

                    if surround_blank:
                        break
                    else:
                        if bounding_box.EndColumn < max_cols:
                            bounding_box.EndColumn += 1
                        if bounding_box.EndRow < max_rows:
                            bounding_box.EndRow += 1
                        if (
                            bounding_box.EndColumn == max_cols
                            and bounding_box.EndRow == max_rows
                        ):
                            break
                new_bounding_boxes = [bounding_box]
            else:
                new_bounding_boxes = bounding_boxes

            sheet.setPrintAreas(new_bounding_boxes)
            style_family = self.document.getStyleFamilies().getByName("PageStyles")
            page_style = style_family.getByName(sheet.PageStyle)
            page_style.setPropertyValue("ScaleToPagesX", 1)
            page_style.setPropertyValue("ScaleToPagesY", 1)

    def export_to_pdf(self, output_url: str) -> None:
        pdf_export_filter = (
            PropertyValue("FilterName", 0, "writer_pdf_Export", 0),
            PropertyValue("Overwrite", 0, True, 0),
        )
        self.document.storeToURL(output_url, pdf_export_filter)

    def close_document(self) -> None:
        self.document.close(True)
        self.document = None
