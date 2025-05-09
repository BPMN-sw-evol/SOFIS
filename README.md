#  Stack OverFlow Issues Searcher - SOFIS

Este es un software que realiza la tarea de Buscar y extraer **todas** las discusiones sobre algún tema, de la plataforma Stack Overflow

SOFIS son las iniciales provenientes de su nombre en inglés: **S**tack **O**ver**F**low **I**ssues **S**earcher. 

## Index

- [Contexto](#contexto)
- [Contribución](#contribución)
- [Funcionalidad General](#funcionalidad-general)
- [Uso de SOFIS](#uso-de-sofis)
  - [Formas de ejecución de SOFIS_CSV](#formas-de-ejecución-de-sofis_csv)
  - [Formas de ejecución de SOFIS_DB](#formas-de-ejecución-de-sofis_db)
- [Requisitos previos](#requisitos-previos)
   - [API de Stack Overflow](#api-de-stack-overflow)
   - [PostgreSQL](#postgresql)
   - [Módulos de Python](#modulos-de-python)
- [Limitations en la API de Stack Overflow](#api-usage-limitations)
- [Resumen](#resumen)
- [API Usage Limitations](#api-usage-limitations)
- [Future Improvements](#future-improvements)

## Contexto
Stack Overflow es una plataforma digital colaborativa de preguntas y respuestas dirigida principalmente a programadores y profesionales de la tecnología. Fundada en 2008, funciona como un espacio donde usuarios pueden plantear dudas técnicas relacionadas con el desarrollo de software, algoritmos, depuración de código y herramientas tecnológicas, recibiendo respuestas de una comunidad global de expertos.

La plataforma se basa en un sistema de votación que permite evaluar la calidad de las contribuciones, fomentando así contenido preciso y útil. Además, integra mecanismos de moderación y reputación para garantizar la confiabilidad de la información. Stack Overflow forma parte del ecosistema Stack Exchange, que abarca diversos temas técnicos y no técnicos, pero destaca por ser el más utilizado en el ámbito de la programación. Su modelo ha sido ampliamente reconocido como un recurso esencial para el aprendizaje y la resolución de problemas en la industria tecnológica. utilizando la API de StackOverflow, consulta las cuestiones que se han creado a partir del 14/01/2014, y almacena los resultados en una base de datos PostgreSQL o en un archivo CSV local.

El propósito de la herramienta es entonces, aprovechar el amplio contenido que guarda la plataforma para crear conocimiento sobre el comportamiento al rededor de determinado tema. Para ésto, el software SOFIS consume  la api que provee Stack Overflow, incorporando el manejo requerido para lograr obtenerlas **todas**. 

## Contribución 

La principal contribución de este software es la entrega al usuario de **todas** las discusiones en las que se menciona el tema de interés. 

Lo anterior tiende un puente entre la comunidad científica relacionada con la tecnología y la programación y la amplia información guardada en la plataforma, de forma que se puedan realizar análisis de comportamiento, tendencias, usos, etc. 

Específicamente el software logra satisfacer los siguientes requerimientos: 
1. Extraer **todas** las conversaciones, 
2. **Excluir** discusiones **mal calificadas**, 
3. **Evitar** resultados **repetidos**. 

El primero de los requerimientos se logra con un algoritmo de control de tiempos y peticiones hasta conseguir todas las discusiones. Lo anterior es necesario debido a que la Api con la cual se preguntan discusiones a la plataforma está configurada con restricciones de seguridad y limitaciones de consumo para evitar que la plataforma se sobrecargue atendiendo peticiones.  

El algoritmo creado, basado en las restricciones, realiza las consultas permitidas durante los segundos y días establecidos por la API, espera el siguiente rango de segundos o de días, según el límite alcanzado y continúa así hasta que logra extraer **todas** las discusiones con el tema especificado. 

Adicionalmente, el software realiza un control de calidad de las discusiones recuperadas. Para ello se basa en los votos de las discusiones y aquellas con votos negativos (menos de cero) son excluidas del resultado. De igual forma, realiza una validación para evitar duplicados en los resultados.   

## Funcionalidad General

SOFIS es un software para utilizar en la línea de comandos de cualquier sistema operativo. Los resultados generados, es decir, las discusiones recuperadas de Stack Overflow, pueden ser obtenidas en un archivo .CSV o en una base de datos en el motor PostgreSQL. 

Para obtener los resultados de una u otra forma, se utiliza la herramienta así: 

- **SOFIS_CSV**: Esta versión genera un archivo CSV con los resultados obtenidos. Ofrece una solución rápida y portable, que le permite recuperar y almacenar las discusiones de StackOverflow en formato CSV, evitando las complejidades de la creación de una base de datos; esta opción es ideal para el análisis directo y la colaboración sin problemas. 

- **SOFIS_DB**: Esta versión utiliza una base de datos PostgreSQL para almacenar los resultados obtenidos. Esta versión proporciona mayor potencia para manejar volúmenes de datos considerables y análisis en profundidad.

## Uso de SOFIS

Como se ha descrito anteriormente, SOFIS ofrece dos versiones, una que crea un archivo .CSV y una que genera registros en una tabla de base de datos. Para cada versión el software tiene una forma de ser ejecutado. A continuación, explicamos la estructura de archivos del software y enseguida cada una de las formas en que SOFIS puede ser ejecutado.  

### Ubicación de los artefactos de software

Este repositorio, que puede descargar o clonar en una carpeta local de su computador en cualquier sistema operativo, tiene la siguiente estructura (vista del explorador de archivos de Windows): 

   <p align="center">
   <img src="https://github.com/BPMN-sw-evol/SOFIS/blob/main/doc/img/SOFIS-RepositoryStructure.PNG?raw=true" alt="SOFIS File Repository Structure" width="550"/>
   </p>

En el folder **doc** se encuentran las imágenes utilizadas en este documento y videos de utilización del software. 

En el folder **SOFIS_CSV** se encuentran los ejecutables que guardan las discusiones en un archivo .CSV 

En el folder **SOFIS_DB** se encuentran los ejecutables que guardan las discusiones en una base de datos de PostgreSQL. 

### Formas de ejecución de **SOFIS_CSV.** 

1. Comando de ejecucion en consola. 


   ![comando de ejecucion](https://github.com/BPMN-sw-evol/SOFIS/blob/main/doc/img/command_execute_console_CSV.png?raw=true) 

      ```
      Texto para que pueda copiar a su consola:  
      
      \SOFIS_CSV_CONSOLA.exe -k «TU_KEY_API» -i «buscar_tema» -u «12-06-2023» -d «\desired\path»</small>  
      ```

2. Script de Python.
   
      ![comando de ejecucion](https://github.com/BPMN-sw-evol/SOFIS/blob/main/doc/img/command_execute_py_CSV.png?raw=true)
      
      ```
      Texto para que pueda copiar a su consola: 
      
      <small>python SOFIS_CSV.py -k «YOUR_API_KEY» -i «search_topic» -u «12-06-2023» -d «\desired\path»</small>
      ```

3. En Windows desde el explorador de archivos puede hacer doble clic en el archivo «SOFIS_CSV_GUI.exe» para ejecutar el programa:

   <p align="center">
   <img src="https://github.com/BPMN-sw-evol/SOFIS/blob/main/doc/img/command_execute_gui_CSV.JPG?raw=true" alt="Comando de ejecución" width="550"/>
   </p>

    >>Como resultado le aparecerá esta interfaz gráfica: 
     
   <p align="center">
   <img src="https://github.com/BPMN-sw-evol/SOFIS/blob/main/doc/img/command_execute_gui_CSV_a.JPG?raw=true" alt="Comando de ejecución" width="500"/>
   </p>
 
     >>En la ventana introduce los parámetros requeridos y le da clic en el botón inferior de "Buscar y Guardar". 


### Formas de ejecución de **SOFIS_DB.**

1. Comando de ejecución en consola.

   Para ejecutar SOFIS. Abra una ventana de terminal o de símbolo del sistema y ejecute el siguiente comando:

   ![comando de ejecucion](https://github.com/BPMN-sw-evol/SOFIS/blob/main/doc/img/command_execute_console_DB.png?raw=true)

      ```
     Texto para que pueda copiar a su consola:  
      
     <small>.\SOFIS_DB_CONSOLE.exe -k "YOUR_API_KEY" -i "search_topic" -d "SOFIS" -u "postgres" -p "1234" -f "12-06-2023"</small>     
     ```

2. Script en Python. 

   ![comando de ejecucion](https://github.com/BPMN-sw-evol/SOFIS/blob/main/doc/img/command_execute_py_DB.png?raw=true)

     ```
     Texto para que pueda copiar a su consola:  

    
    >><small>python SOFIS_DB.py -k "YOUR_API_KEY" -i "search_topic" -d "SOFIS" -u "postgres" -p "1234" -f "12-06-2023"</small>  
     ```

3. En Windows desde el explorador de archivos puede hacer doble clic en el archivo «SOFIS_DB.exe» para ejecutar el programa:

   <p align="center">
   <img src="https://github.com/BPMN-sw-evol/SOFIS/blob/main/doc/img/command_execute_gui_DB.png?raw=true" alt="Comando de ejecución" width="550"/>

   >>Como resultado le aparecerá esta interfaz gráfica: 
     
   <p align="center">
   <img src="https://github.com/BPMN-sw-evol/SOFIS/blob/main/doc/img/command_execute_gui_DB_a.PNG?raw=true" alt="Comando de ejecución" width="500"/>
   </p>
 
     >>En la ventana introduce los parámetros requeridos y le da clic en el botón inferior de "Search and Save". 

**NOTAS**

- Cuando ejecute los archivos «.py» o «.bat» para almacenar discusiones en formato CSV, se creará el archivo «SQ.pars.<»search_topic«>.txt». Este archivo almacena los parámetros de la última consulta realizada para el tema de búsqueda utilizado.

- Cuando ejecute la versión que guarda las discusiones en una base de datos, para consultar la información puede usar la siguiente sentencia SQL en pgAdmin 4:

  ```
    SELECT \* FROM SOFIS_QUERY WHERE title ILIKE '%search_topic%';
  ```

## Requisitos previos. 

Debido a que este software consume y utiliza servicios que proveen terceros, es necesario cumplir algunos requisitos para su utilización. A continuación, se detallan cada uno de ellos: 

### API de Stack Overflow 

Para utilizar la API de StackOverflow y realizar solicitudes es necesario contar con una "llave" de la API. A continuación, indicamos los pasos a seguir para obtener las credenciales necesarias:

- Registrar una cuenta en [Stack Apps](https://stackapps.com/users/login).
- Registrar su aplicación para obtener las credenciales de la API en [Stack Apps - Registrar una aplicación](https://stackapps.com/apps/oauth/register). Aquí obtendrás un ID de cliente y una clave secreta para la autenticación _OAuth_ en Stack Overflow. Deberá proporcionar esta clave cuando utilice **SOFIS**.  

Si necesita consultar los datos de su API de Stack Overflow, vaya a [Your Apps](https://stackapps.com/apps/oauth) en [stackapps](stackapps.com). 

### PostgreSQL

Si va a utilizar la versión de SOFIS que recupera las discusiones y las guarda en una base de datos((SOFIS_DB)), debe saber que el software utiliza PostgreSQL y que debe seguir los siguientes pasos para poder utilizar esta version de SOFIS: 

- **Instalar PostgreSQL**: Descargue e instale la versión estable o la última versión desde el sitio oficial de descargas de PostgreSQL [sitio oficial de PostgreSQL](https://www.postgresql.org/download/).

- **Crear la base de datos** Uitilice pgAdmin 4 (viene incluido con PostgreSQL), y cree una base de datos llamada `SOFIS`.

- **Crear la tabla**: En la base de datos `SOFIS` database, ejecute el script de creación de la tabla SOFIS, donde serán guardadas las dicusiones recuperadas de Stack Overflow. El script se encuentra disponible en el repositorio: [SOFIS_Query.sql](https://github.com/BPMN-sw-evol/SOFIS/blob/main/SOFIS_DB/SOFIS_Query.sql) y este es su contenido: 

   ````sql
   CREATE TABLE SOFIS (
      id_discussion SERIAL PRIMARY KEY,
      topic VARCHAR(25),
      title VARCHAR(255),
      link VARCHAR(255),
      score INTEGER,
      answer_count INTEGER,
      view_count INTEGER,
      creation_date DATE,
      tags VARCHAR(255)
   );
   ````

### Módulos de Python

- **Python**: Instale Python desde su sitio oficial [Python](https://www.python.org/downloads/) o instale la extensión de Python in VS Code.

- **Módulos de Python requeridos**:
   - requests (para realizar solicitudes HTTP): `pip install requests`
   - psycopg2-binary (sólamente para la versión SOFIS_DB): `pip install psycopg2-binary`

## Uso del código fuente

Si planea utilizar el código fuente de SOFIS tenga en cuenta: 

- **Editor de código**: Le recomendamos usar Visual Studio Code (VS Code). Puede descargarlo de [sitio oficial de VS](https://code.visualstudio.com/download).

- **GIT**: Instale el sistema de control de versiones GIT de su sitio oficial [sitio oficial de GIT](https://git-scm.com/downloads).

- **Clone el repositorio**: Esto puede hacerlo con el comando: `git clone https://github.com/BPMN-sw-evol/SOFIS.git`.

## Resumen

SOFIS recupera de la plataforma especializada en temas tecnológicos y de desarrollo Stack Overflow, las discusiones relacionadas con un tema de búsqueda específico, que se hayan presentado a partir de determinada fecha. Almacena estas discusiones en un archivo CSV o en una base de datos local utilizando PostgreSQL. 

SOFIS comprueba si cada discusión ya existe en el archivo CSV o en la base de datos, si no es así, y tiene una puntuación mayor o igual a cero, la agrega. Además, proporciona información sobre el número de preguntas encontradas, insertadas, omitidas debido a votos negativos y omitidas debido a que ya existen en el archivo CSV o en la base de datos .

En el archivo CSV o en la base de datos SOFIS almacena los siguientes atributos de cada discusión:

| Atributo      | Descripción                                    |
| ------------- | ---------------------------------------------- |
| id_discussion | Identificador único de la discusión            |
| title         | Título de la discusión                         |
| link          | Enlace a la discusión en StackOverflow website |
| score         | Puntaje de la discusión                        |
| answer_count  | Número de respuestas para la discusión         |
| view_count    | Number of vistas de la discusión               |
| creation_date | Fecha de creación de la discusión              |
| tags          | Etiquetas relacionadas con la discusión        |

Este software es una herramienta que se centra en la búsqueda de discusiones en StackOverflow cuyos títulos contengan una palabra específica enviada por parámetro, a partir de determinada fecha. Este enfoque garantiza que los datos obtenidos sean más relevantes contextualmente según el interés de quien realiza la búsqueda. Nostros lo usamos para encontrar las comunidades alrrededor de diferentes plataformas para gestión de procesos (BPMs de sus iniciales en inglés Business Process Management Systems) y poder comparar sus tamaños y nivel de actividad. 

## Limitaciones de la API de Stack Overflow

1. Máximo 30 solicitudes  per segundo.
2. Máximo 10,000 solicitudes por día.  
3. Si el límite diario es excedido, la api retorna un error HTTP 429.
4. El límite diario se reinicia desde la medianoche. 

## Mejoras futuras

1. Implementar el uso de una base de datos en la nube, para mejorar la accesibilidad a los resultados y la escabilidad de su uso en temas con muchos más resultados que los que nosotros buscamos. 

2. Agregar funcionalidad para actualizar registros individualmente según las necesidades del usuario de la herramienta. 
