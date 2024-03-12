import json

# Cargar los archivos JSON
with open(r"C:\Users\diego\Desktop\TFG MOONBOARD\datasets\2017_problems_40.json", 'r') as file1:
    json1 = json.load(file1)

with open(r"C:\Users\diego\Desktop\TFG MOONBOARD\datasets\2017_problems_list_40.json", 'r') as file2:
    json2 = json.load(file2)

# Crear un diccionario para facilitar la búsqueda en el segundo JSON
json2_dict = {element['Name']: element for element in json2.values()}

# Lista para almacenar los elementos ordenados
result_list = []

# Recorrer cada elemento del primer JSON
for problem in json1.values():
    nombre = problem.get('Name')

    # Buscar el elemento correspondiente en el segundo JSON usando la coincidencia parcial
    matching_element = next((element for element_name, element in json2_dict.items() if element_name in nombre), None)

    # Si se encuentra un elemento correspondiente, agregar los campos adicionales
    if matching_element:
        problem['UserGrade'] = matching_element.get('UserGrade')
        problem['Repeats'] = matching_element.get('Repeats')
        problem['Method'] = matching_element.get('Method')
        
    # Eliminar el campo "Sended"
    if 'Sended' in problem:
        del problem['Sended']

    # Agregar el problema a la lista resultante
    result_list.append(problem)

# Guardar el resultado actualizado en un nuevo archivo JSON con índices en orden ascendente
with open(r"C:\Users\diego\Desktop\TFG MOONBOARD\datasets\2017_problems_combined_40.json", 'w') as result_file:
    json.dump(result_list, result_file, indent=2)
