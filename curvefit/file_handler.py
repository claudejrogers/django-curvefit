import xlrd

def file_handler(filepath, extn):
    """
    Read data from file. Use xlrd to handle .xls files. Return x and y values
    and a message. I think the msg was only debugging, but I don't remember.
    """
    xdata, ydata = [], []
    msg = ''
    if extn == '.xls':
        wb = xlrd.open_workbook(filepath)
        sh = wb.sheet_by_index(0)
        x_raw = sh.col_values(0)
        y_raw = sh.col_values(1)
        for i in range(min(len(x_raw), len(y_raw))):
            if type(x_raw[i]) == float and type(y_raw[i]) == float:
                xdata.append(x_raw[i])
                ydata.append(y_raw[i])
    else:
        x_raw, y_raw = [], []
        with open(filepath, "rU") as f:
            for line in f:
                if extn == '.txt':
                    row = line.split()
                elif extn == '.csv':
                    row = line.strip().split(',')
                x_raw.append(row[0])
                y_raw.append(row[1])
        for i in range(len(x_raw)):
            try:
                x, y = float(x_raw[i]), float(y_raw[i])
                xdata.append(x)
                ydata.append(y)
            except ValueError:
                continue
    return xdata, ydata, msg