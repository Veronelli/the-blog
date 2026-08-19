## Why

Los usuarios no cuentan con una identidad pública estructurada ni con una forma consistente de compartir sus redes sociales. Los enlaces libres no permiten reutilizar reglas de captura ni validar los valores de cada plataforma, y exponen controles que deben quedar reservados al personal staff.

## What Changes

- Incorporar configuraciones de redes sociales y variables reutilizables, administrables exclusivamente por usuarios staff desde Django admin.
- Permitir que cada configuración defina nombre, `template_url`, `icon_url` y las variables que utiliza.
- Validar cada valor ingresado contra la expresión regular de su variable antes de publicarlo.
- Incorporar un perfil público asociado al usuario con `public_username` único, nombre, apellido, título, subtítulo, especialidad, descripción corta, foto y redes sociales instanciadas.
- Permitir a los usuarios gestionar sus propias instancias de red social y valores desde el dashboard.
- Exponer la información del perfil mediante su `public_username`, sin permitir que un usuario no staff cree ni modifique definiciones de redes o variables.

## Capabilities

### New Capabilities
- `social-variables`: Variables reutilizables y sus instancias validadas por expresión regular.
- `social-network-catalog`: Configuraciones de redes sociales, variables asociadas e instancias de configuración por usuario.
- `public-user-profile`: Perfil público identificado por `public_username` y gestión desde el dashboard de instancias de redes sociales.

### Modified Capabilities

Ninguna.

## Impact

- Nuevos modelos y migraciones para variables, configuraciones de redes sociales, instancias de usuario, perfiles públicos y valores de variables.
- Vistas, formularios y plantillas del dashboard y de la presentación pública del perfil.
- Configuración de Django admin para las definiciones de redes y variables.
- Pruebas de permisos, expresiones regulares, configuración de variables, instancias y visibilidad pública.
