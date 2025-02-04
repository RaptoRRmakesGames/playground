from molar_mass_calculator import app 
from flask import Flask, render_template, redirect, request
import copy

class Table:
    
    def __init__(self, data: list):
        self.table = copy.deepcopy(data)  # Create a deep copy of the input data
        self.n = len(self.table)
        
    def visualise(self) -> str:
        res = ''
        
        for col in self.table:
            res += f"{col}\n"
        return res
        
    def determinant(self) -> float:
        if self.n == 2:
            # Base case for 2x2 matrix
            return self.table[0][0] * self.table[1][1] - self.table[0][1] * self.table[1][0]

        # Recursive case
        determinant = 0
        chosen_row_index = 0  # Always expand along the first row

        for chosen_col_index in range(self.n):
            # Calculate the sign for the current cofactor
            sign = (-1) ** chosen_col_index

            # Generate the submatrix by excluding the chosen row and column
            submatrix = [
                [val for j, val in enumerate(row) if j != chosen_col_index]
                for i, row in enumerate(self.table) if i != chosen_row_index
            ]

            # Calculate the determinant of the submatrix
            sub_determinant = Table(submatrix).determinant()

            # Add the current cofactor to the total determinant
            determinant += sign * self.table[chosen_row_index][chosen_col_index] * sub_determinant

        return determinant
    
    def determinant_fast(self) -> float:
        matrix = [row[:] for row in self.table]  # Create a copy of the matrix
        n = self.n
        det = 1

        for i in range(n):
            # Find the pivot for column i
            max_row = i
            for k in range(i + 1, n):
                if abs(matrix[k][i]) > abs(matrix[max_row][i]):
                    max_row = k
            
            # If the pivot is 0, the determinant is 0
            if matrix[max_row][i] == 0:
                return 0
            
            # Swap the current row with the pivot row if necessary
            if max_row != i:
                matrix[i], matrix[max_row] = matrix[max_row], matrix[i]
                det *= -1  # Swapping rows changes the sign of the determinant
            
            # Multiply the diagonal element to the determinant
            det *= matrix[i][i]

            # Eliminate entries below the pivot
            for k in range(i + 1, n):
                factor = matrix[k][i] / matrix[i][i]
                for j in range(i, n):
                    matrix[k][j] -= factor * matrix[i][j]
        
        return det


@app.route('/determinant_fast', methods=['GET', 'POST'])
def determinant_fast():
    
    if request.method == 'POST':
        n = int(request.form.get('n'))
        data = [[[] for x in range(n)] for i in range(n)]
        max_row,max_col = 2,2
        
        for key in dict(request.form):
            if 'num' not in key : continue
            
            print(key.strip('num_'))
            col, row = key.strip('num_').split('_')
            col, row = int(col), int(row)
            max_row = max(row, max_row)
            max_col = max(col, max_col)
            print(col, row)
            data[col-1][row-1] = int(request.form.get(key))
            
        print(data)
            
        obj = Table(data)
        
        return render_template('determinant.html', result=f'={obj.determinant_fast()}\n{obj.visualise()}'.replace('\n', '<br>'), extra_text='<a href="/determinant">Try Recursive Method</a>', which='Gaussian Elimination - O(n^3)')
    
    return render_template('determinant.html', result='', extra_text='<a href="/determinant">Try Recursive Method</a>', which='Gaussian Elimination - O(n^3)')

@app.route('/determinant', methods=['GET', 'POST'])
def determinant():
    
    if request.method == 'POST':
        n = int(request.form.get('n'))
        data = [[[] for x in range(n)] for i in range(n)]
        max_row,max_col = 2,2
        
        for key in dict(request.form):
            if 'num' not in key : continue
            
            print(key.strip('num_'))
            col, row = key.strip('num_').split('_')
            col, row = int(col), int(row)
            max_row = max(row, max_row)
            max_col = max(col, max_col)
            print(col, row)
            data[col-1][row-1] = int(request.form.get(key))
            
        print(data)
            
        obj = Table(data)
        
        return render_template('determinant.html', result=f'={obj.determinant()}\n{obj.visualise()}'.replace('\n', '<br>'), extra_text='<a href="/determinant_fast">Try Gaussian Method</a>', which='Recursive - O(n!)')
    
    return render_template('determinant.html', result='', extra_text='<a href="/determinant_fast">Try Gaussian Method</a>', which='Recursive - O(n!)')