from npyscreen import GridColTitles
'''
USEFUL FUNCTIONS
'''
def is_number(number):
    try:
        return bool(float(number))
    except (ValueError, TypeError):
        return False

def formatted_values(values_dict):
    values=[]
    for element in values_dict:
        values.append(str(element)+' : '+str(values_dict[element]))
    return values

def stock_report_cleaned_matrix(values):

    cleaned_list=[[values[0][i] for i in range(len(values[0]))]]
    for i in range(1, len(values)):
        line=[]
        for j, cell in enumerate(values[i]):
            if cell!=values[i-1][j] or cell==0:
                if j!=1:
                    try:
                        cell=float("{0:.4f}".format(cell)) #per la precisione
                    except (TypeError, ValueError):
                        pass
                line.append(cell)
            else:
                line.append('')
        cleaned_list.append(line)
    return cleaned_list



#da spostare
'''
GRID CLASSES
'''

class ReportGrid(GridColTitles):
    default_column_number = 10

'''
COSTUM ERROR DECLARATION
'''

class NoInputException(Exception):
    pass
