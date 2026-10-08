# Local AI Repository Engineer

Repository documentation and review assistant using CrewAI.

**¿Qué es CrewAI?**

CrewAI es un framework de Python para construir sistemas de agentes de IA que colaboran entre sí.

La idea básica es pasar de:

```text
Usuario → LLM → respuesta
```

a algo como:

```text
Usuario → Orquestador → Agente investigador → Agente analista → Agente programador → Agente revisor → Resultado
```

CrewAI proporciona dos conceptos principales:

- Crews → equipos de agentes que colaboran de forma relativamente autónoma.
- Flows → workflows controlados, con estados, condiciones, branching, etc.

Esto es importante: no necesitas varios modelos distintos. Puedes tener varios agentes usando el mismo modelo local de Ollama, pero con diferentes roles, prompts, herramientas y objetivos.

## Idea: AI Repository Engineer

- Input: `./my-project`
- Output:
  - analiza la estructura
  - detecta el lenguaje
  - identifica dependencias
  - analiza arquitectura
  - revisa tests
  - busca problemas
  - genera documentación
  - propone mejoras

Mi propuesta para empezar ahora

Vamos a hacerlo paso a paso, y no te voy a soltar 500 líneas de código de golpe.

Sprint 1

- [x] Crear repositorio
- [x] Python 3.12 + venv
- [x] Instalar CrewAI
- [x] Conectar CrewAI → Ollama
- [x] Crear primer Agent
- [x] Crear RepositoryScanner
- [x] Analizar un repositorio real
- [x] Generar repository_analysis.md

Sprint 2

- [ ] Architecture Agent
- [ ] Security Agent
- [ ] Testing Agent
- [ ] Reviewer Agent
- [ ] Crew

Sprint 3

- [ ] CrewAI Flow
- [ ] Git
- [ ] RAG
- [ ] Memory
- [ ] CLI completa

Sprint 4

- [ ] VS Code
- [ ] Code modifications
- [ ] Test generation
- [ ] Automatic fixes

## Arquitectura

Ejemplo sencillo: analizar un repositorio.

```text
                    ┌──────────────────┐
                    │    CrewAI Flow   │
                    └────────┬─────────┘
                             │
                ┌────────────▼────────────┐
                │     Repo Analyzer       │
                └────────────┬────────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
       ┌─────────┐      ┌──────────┐    ┌──────────┐
       │ Python  │      │ Security │    │  Tests   │
       │ Agent   │      │  Agent   │    │  Agent   │
       └────┬────┘      └────┬─────┘    └────┬─────┘
            │                 │               │
            └─────────────────┼───────────────┘
                              ▼
                       ┌─────────────┐
                       │   Reviewer  │
                       └──────┬──────┘
                              ▼
                       documentation.md
```

**Target:**

```text
                 ┌─────────────────────┐
                 │        CLI           │
                 │ repo-engineer <repo> │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │     CrewAI Flow     │
                 └──────────┬──────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        Repository      Architecture    Code
        Analyzer           Agent        Agent
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                      Review Agent
                            │
                            ▼
                    Documentation Agent
                            │
                            ▼
                    reports/final.md
                            │
                            ▼
                         Ollama
                            │
                            ▼
                     Intel Arc 140V
```

## Sprint 1: El agente puede inspeccionar el filesystem mediante una Tool y razonar sobre lo que encuentra.

### Componentes

Se crea el primer **Agent**, algo sencillo, dentro de `src/repository_engineer/main.py`.

Para configurar el modelo local es necesario decirle explícitamente a CrewAI "No quiero OpenAI. Quiero utilizar mi modelo de Ollama". Para ello instalaremos `pip install litellm` y configuraremos nuestro LLM mediante Ollama. No vamos a montar un servidor LiteLLM, lo utilizaremos únicamente como capa de compatibilidad de Python para que CrewAI pueda comunicarse con diferentes proveedores de modelos.

Todavía falta una cosa: una **Task**. Importante: **Un Agent define quién es y qué sabe hacer. Una Task define qué queremos que haga.**

Finalmente, creamos nuestras primeras **Tools**. Una tool en CrewAI es una habilidad, función o interfaz que un agente de inteligencia artificial puede utilizar para realizar acciones concretas, interactuar con el mundo exterior o procesar información más allá de su conocimiento interno.

- **RepositoryScanner**: Hacer que el agente pueda inspeccionar un repositorio real.

No queremos que nuestra primera versión sea demasiado inteligente.

Simplemente:

1. recibir una ruta
2. comprobar que existe
3. recorrer directorios
4. ignorar basura
5. identificar archivos
6. detectar lenguajes
7. devolver un resumen

Nuestro scanner devuelve la estructura, pero no el contenido del código. El agente sabe que existen, pero no sabe qué contienen.

- **FileReader**: Hacer que el agente pueda leer archivos específicos.

Y entonces podremos pedir:

"Analiza cómo funciona la autenticación de este proyecto."

El agente podrá:

1. escanear el repo
2. encontrar archivos relevantes
3. leerlos
4. analizarlos
5. producir una explicación

- **ReportWriter**: Permita al agente o a nuestra aplicación guardar el resultado en: `reports/repository_analysis.md`.

### Objetivo final

- Pre-Ejecución

Hay una pequeña cuestión con los imports:

Para que Python encuentre repository_engineer, ejecutaremos el proyecto con: `$env:PYTHONPATH="src"`. Y después: `python -m repository_engineer.main .`.

Más adelante solucionaremos esto correctamente con pyproject.toml, pero para este checkpoint no necesitamos complicarlo.

- Ejecutar

```bash
python src\repository_engineer\main.py .\mi-repositorio
```

- Obtener

```text
Repository: my-project

Languages:
- Python
- JavaScript

Files:
- src/main.py
- src/api.py
- tests/test_api.py
- package.json
- README.md

Directories:
- src/
- tests/

Configuration:
- requirements.txt
- package.json

Tests:
- tests/test_api.py
```

La idea importante es que el LLM no va a recorrer el disco por sí mismo. Nosotros le proporcionaremos herramientas controladas para hacerlo.
