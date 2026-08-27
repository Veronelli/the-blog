## Why

Un usuario autenticado sin `PublicProfile` no puede completar su identidad pública ni acceder de forma segura al dashboard. El flujo debe crear el perfil desde la sesión autenticada y permitir el dashboard únicamente después de completar los datos obligatorios, sin que el acceso de staff o superusuario omita este requisito.

## What Changes

- Redirigir a toda cuenta autenticada que no tenga un perfil público, incluidas las cuentas staff y superusuario, al formulario de creación antes de permitirle usar el dashboard.
- Añadir un panel de autoservicio basado en las vistas, componentes y estilos nativos de Django admin, sin plantillas HTML propias, para crear el perfil público asociado exclusivamente al usuario autenticado de la sesión.
- Añadir un dashboard protegido dentro de ese panel que sólo esté disponible para usuarios con un perfil público completo.
- Actualizar el alcance de `PublicProfile` para incluir el flujo web de alta y la inmutabilidad de su usuario autenticado asociado.

## Capabilities

### New Capabilities

- `public-profile-onboarding`: Flujo web autenticado para crear el perfil público pendiente y controlar el acceso al dashboard.

### Modified Capabilities

- `public-user-profile`: El perfil público se crea mediante el flujo de onboarding para el usuario autenticado y su asociación de usuario no puede modificarse.

## Impact

- Configuración de un panel de autoservicio de Django admin, su formulario de `PublicProfile` y sus controles de acceso por propietario.
- Enrutamiento posterior al inicio de sesión hacia el panel y controles de acceso del dashboard para toda cuenta autenticada.
- Modelo y pruebas de `profiles.PublicProfile`, junto con pruebas de integración del flujo admin para usuarios normales, staff y superusuarios.
