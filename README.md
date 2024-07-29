# Prueba Técnica Phicus: TIC TAC TOE

## Requisitos

- Python 3.10 o superior
- Poetry (para la gestión de dependencias y entornos virtuales) __Recomendado__
```python
pip install poetry
```
Si se desea utilizar otra herramienta para el manejo de entornos virutales, también se dispone del fichero "requirements.txt".

Comando para actualizar el fichero "requirements.txt" a partir de poetry:
```bash
poetry export --without-hashes --format=requirements.txt > requirements.txt
```

## Instalación

1. **Clonar el Repositorio**

   ```bash
   git clone https://github.com/vLorente/prueba_tecnica_phicus
   cd prueba_tecnica_phicus

2. **Instalar dependencias**
   Instalar todas las dependencias del proyecto:
   ```bash
   poetry install
   ```
3. **Activar el entorno virtual**
   ```bash
   poetry shell
   ```
4. **Configurar Base de datos**
   Realizar las migraciones necesarias para confirurar la base de datos:
   ```bash
   python manage.py makemigrations
   ```
   ```bash
   python manage.py migrate
   ```
5. **Crear superusuario (Opcional)**
   Para acceder al paner de administración de Django, se puede crear un nuevo superusuario:
   ```bash
   python manage.py createsuperuser
   ```

## Uso
>**Importante**: durante todo el proceso se debe encontrar dentro del entorno virutal.
### Ejecutar el servidor
Iniciar el servidor de desarrollo de Django:
```python
python manage.py runserver
```

### Jugar a TIC TAC TOE
El script play.py proporciona una interfaz de línea de comandos para interactuar con la API.

1. **El servidor debe estar arrancado**
2. **Ejecutar el script**
   ```bash
   python play.py
   ```

## Testing
Para ejecutar los tests, utiliza el siguiente comando:

```bash
python manage.py test
```