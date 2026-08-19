## Purpose

Ofrecer una identidad pública configurable para cada usuario y permitirle mantener sus datos y enlaces sociales desde su dashboard.

## ADDED Requirements

### Requirement: Perfil público identificado por nombre de usuario público
El sistema SHALL mantener un perfil público por usuario que incluya un `public_username` único, nombre, apellido, título, subtítulo, especialidad, descripción corta, `photo_url` opcional y redes sociales instanciadas. Cuando se proporcione, `photo_url` MUST ser una URL válida de una imagen externa. El `public_username` SHALL identificar la presentación pública del perfil y la información guardada SHALL estar disponible para visitantes.

#### Scenario: Visitante consulta un perfil configurado
- **WHEN** un visitante accede a la presentación pública mediante el `public_username` de un perfil configurado
- **THEN** el sistema muestra los campos públicos disponibles y sus redes sociales construidas

#### Scenario: Usuario intenta elegir un nombre público existente
- **WHEN** un usuario intenta guardar un `public_username` ya asignado a otro perfil
- **THEN** el sistema rechaza el cambio y conserva el nombre público existente

#### Scenario: Usuario guarda una URL de foto válida
- **WHEN** un usuario autenticado proporciona una `photo_url` válida al actualizar su perfil
- **THEN** el sistema guarda la URL y muestra la imagen externa en su presentación pública

### Requirement: Gestión de perfil desde el dashboard
El sistema SHALL permitir a un usuario autenticado crear y actualizar únicamente su propio perfil público desde el dashboard. El usuario MUST NOT poder modificar el perfil público de otro usuario.

#### Scenario: Usuario actualiza su información pública
- **WHEN** un usuario autenticado guarda cambios válidos en los campos de su perfil desde el dashboard
- **THEN** el sistema persiste los cambios y los refleja en su presentación pública

#### Scenario: Usuario intenta modificar otro perfil
- **WHEN** un usuario autenticado intenta actualizar el perfil asociado a otro usuario
- **THEN** el sistema rechaza la operación sin modificar el perfil objetivo

### Requirement: Gestión de instancias de redes sociales del perfil
El sistema SHALL permitir a un usuario autenticado añadir, actualizar y archivar las instancias de redes sociales que le pertenecen desde el dashboard. Para cada instancia, el usuario SHALL proporcionar valores únicamente para variables asociadas a la configuración seleccionada. Cada URL e ícono publicados MUST obtenerse de la configuración y los valores validados de sus variables. El dashboard MUST NOT permitir borrar físicamente una instancia ni cambiar su autor.

#### Scenario: Usuario añade una instancia de red social a su perfil
- **WHEN** un usuario selecciona una configuración disponible y proporciona valores válidos para sus variables asociadas desde el dashboard
- **THEN** el sistema guarda la instancia y muestra su URL construida en el perfil público

#### Scenario: Usuario archiva una instancia de red social
- **WHEN** un usuario archiva una de las instancias de red social de su perfil desde el dashboard
- **THEN** el sistema deja de mostrar la URL de esa instancia en su perfil público y conserva su registro archivado
