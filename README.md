# Contribuir al proyecto Neon_linde

## Descripción rápida
Este proyecto contiene scripts y configuraciones para procesar PDFs y generar contenido multimodal con Gemini. ¡Tu ayuda es bienvenida!

## Empezar a contribuir
1. **Clona el repositorio**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd Neon
   ```
2. **Instala las dependencias**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/macOS
   pip install -r requirements.txt
   ```
3. **Ejecuta los tests** (si existen)
   ```bash
   pytest
   ```
4. **Crea una rama** para tu cambio
   ```bash
   git checkout -b nombre-de-tu-funcionalidad
   ```
5. **Haz tus cambios** y **commit** siguiendo el estilo de mensajes:
   ```bash
   git add .
   git commit -m "feat: breve descripción del cambio"
   ```
6. **Abre un Pull Request**
   - Asegúrate de que tu PR describa claramente qué problema resuelve y cómo probarlo.
   - Pide revisión a al menos un mantenedor.

## Buenas prácticas
- Mantén el código **pep8** (usa `flake8` o `black`).
- Añade o actualiza pruebas unitarias para cualquier nueva funcionalidad.
- Actualiza la documentación si es necesario.
- Evita commits grandes; haz cambios atómicos y bien descritos.

## Licencia
Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---
*¡Gracias por tu contribución!*
