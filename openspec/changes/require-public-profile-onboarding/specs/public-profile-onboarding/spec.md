## Purpose

Permitir que cada usuario autenticado complete su identidad pública antes de acceder a las funciones del dashboard.

## ADDED Requirements

### Requirement: Redirección de onboarding para perfiles pendientes
El sistema SHALL dirigir a toda cuenta autenticada que no tenga un perfil público al flujo de creación de perfil antes de concederle acceso a cualquier ruta del dashboard, independientemente de que tenga privilegios staff o de superusuario. La ruta de creación del perfil y la ruta de cierre de sesión MUST permanecer disponibles para ese usuario. Un usuario autenticado que ya tenga un perfil público SHALL poder acceder al dashboard sin pasar por dicho flujo.

#### Scenario: Usuario sin perfil inicia sesión
- **WHEN** un usuario autenticado sin perfil público intenta acceder al dashboard después de iniciar sesión
- **THEN** el sistema lo dirige al formulario de creación de su perfil público y no muestra el dashboard

#### Scenario: Usuario con perfil accede al dashboard
- **WHEN** un usuario autenticado con perfil público completo intenta acceder al dashboard
- **THEN** el sistema muestra el dashboard sin redirigirlo al formulario de creación

#### Scenario: Usuario staff sin perfil inicia sesión
- **WHEN** una cuenta autenticada con privilegios staff y sin perfil público intenta acceder al dashboard
- **THEN** el sistema la dirige al formulario de creación de su propio perfil público y no muestra el dashboard

#### Scenario: Usuario sin perfil abre una ruta interna del dashboard
- **WHEN** un usuario autenticado sin perfil público solicita una ruta del dashboard distinta del formulario de creación o del cierre de sesión
- **THEN** el sistema lo dirige al formulario de creación de su propio perfil público

### Requirement: Formulario de creación vinculado a la sesión
El sistema SHALL mostrar a los usuarios autenticados sin perfil público un formulario para proporcionar los datos obligatorios de su perfil mediante la interfaz y los componentes nativos de Django admin. El sistema MAY usar un único override de template de Django admin, limitado al formulario de `PublicProfile`, para ocultar la navegación de breadcrumbs y la barra lateral. El formulario MUST no permitir seleccionar ni proporcionar un usuario de autenticación; el perfil creado MUST asociarse al usuario autenticado de la sesión.

#### Scenario: Usuario crea su propio perfil
- **WHEN** un usuario autenticado sin perfil envía datos de perfil válidos
- **THEN** el sistema crea un perfil público asociado a ese usuario autenticado

#### Scenario: Formulario no expone selección de usuario
- **WHEN** un usuario autenticado visualiza el formulario de creación de perfil
- **THEN** el formulario no muestra un selector ni un campo editable para el usuario de autenticación

#### Scenario: Formulario usa componentes nativos de Django admin
- **WHEN** un usuario autenticado sin perfil abre el formulario de creación
- **THEN** el sistema muestra los estilos, componentes y errores de validación propios de Django admin

#### Scenario: Formulario oculta navegación administrativa no necesaria
- **WHEN** un usuario autenticado abre el formulario de creación o edición de su perfil público
- **THEN** el sistema no muestra breadcrumbs ni barra lateral y conserva el navbar con la opción de cerrar sesión

### Requirement: Acceso al dashboard tras completar el perfil
El sistema SHALL conceder acceso al dashboard sólo después de que el usuario autenticado haya creado su perfil público con todos los datos obligatorios válidos. Si los datos enviados no son válidos, el sistema MUST mostrar los errores y mantener al usuario en el flujo de creación sin conceder acceso al dashboard.

#### Scenario: Creación completada correctamente
- **WHEN** el usuario envía todos los datos obligatorios válidos del perfil
- **THEN** el sistema guarda el perfil y dirige al usuario al dashboard

#### Scenario: Datos de perfil inválidos
- **WHEN** el usuario envía datos obligatorios ausentes o inválidos
- **THEN** el sistema no crea el perfil, muestra los errores de validación y no permite acceder al dashboard
