## Context

El proyecto usa el modelo `auth.User` de Django, solo tiene la aplicación `posts` y no expone aún rutas de dashboard ni perfiles públicos. Véanse `proposal.md` y los delta specs para la motivación y los requisitos de comportamiento.

## Goals / Non-Goals

**Goals:**
- Añadir una aplicación de perfiles que concentre las definiciones de variables, configuraciones de redes sociales, la información pública y las instancias de cada usuario.
- Mantener la administración de definiciones separada de la edición que realiza un usuario sobre sus propias instancias.
- Validar los valores de variables tanto en el formulario como en el modelo para que no puedan persistirse valores inválidos por rutas alternativas.
- Exponer rutas explícitas para editar el perfil propio y consultar un perfil público.
- Aplicar TDD a cada capacidad mediante ciclos red-green-refactor antes de incorporar su funcionalidad.

**Non-Goals:**
- No sustituir el modelo `auth.User` existente ni implementar registro, autenticación o recuperación de cuenta.
- No importar automáticamente datos desde proveedores externos ni verificar la propiedad de una cuenta social.
- No incluir un sistema de seguimiento, analíticas, orden personalizado de enlaces o una API pública en esta primera entrega.

## Decisions

### Aplicación y modelo de datos dedicados

Se creará una aplicación `profiles` con cinco modelos. `Variable` y `VariableInstance` forman una capacidad independiente: la primera define un identificador reutilizable, `label`, descripción y expresión regular; la segunda persiste un valor validado asociado a una instancia de red social. `SocialNetworkConfig` es la única definición de red social: contiene nombre, `template_url`, `icon_url` y las variables que utiliza. `PublicProfile`, relacionado uno a uno con `auth.User`, contiene los datos públicos, un `public_username` único y una `photo_url` opcional. `SocialNetworkInstance` representa una configuración elegida por un usuario, conserva su autor inmutable y es la única fuente de propiedad para sus instancias de variables.

Las relaciones serán `SocialNetworkConfig N:M Variable`, `auth.User 1:N SocialNetworkInstance N:1 SocialNetworkConfig` y `SocialNetworkInstance 1:N VariableInstance N:1 Variable`. Esta separación permite reutilizar variables entre configuraciones, que una configuración solicite varios valores y que un usuario tenga varias instancias. La spec `social-variables` define el contrato de variables e instancias; la spec de configuraciones de redes sociales define qué variables consume cada configuración. Se descarta añadir campos al usuario actual porque Django ya usa `auth.User` y cambiarlo requeriría una migración de autenticación innecesaria.

### Plantillas de URL y validación centralizada

Cada `SocialNetworkConfig` almacenará `template_url` e `icon_url`, y asociará las variables que puede consumir. La configuración validará que toda referencia de `template_url` pertenece a una de sus variables asociadas. Un validador propio será llamado por `VariableInstance.clean()` y por los formularios para comprobar una coincidencia completa contra el `regex` de la variable, además de comprobar que la variable está asociada a la configuración de su `SocialNetworkInstance`. La URL pública y el ícono se derivarán de la configuración y de los valores validados.

Se descarta guardar una URL arbitraria porque impediría garantizar la relación entre la plataforma, sus variables y sus valores validados. También se descarta codificar las redes o variables en una lista estática, ya que el personal staff debe poder administrarlas sin desplegar código.

### Límites de acceso por superficie

`Variable` y `SocialNetworkConfig` serán registrados en Django admin y sus operaciones de escritura estarán restringidas por los permisos estándar de Django, disponibles solo a staff. Las vistas del dashboard exigirán autenticación y resolverán siempre el perfil y las instancias desde `request.user`; no recibirán una identidad de propietario editable. La pantalla pública buscará por `public_username` y será solo de lectura.

Esta estrategia reutiliza los límites de seguridad ya provistos por el admin y evita que un parámetro de URL permita editar perfiles ajenos. Se descarta exponer las configuraciones de redes o variables mediante formularios de dashboard porque contradice la separación de responsabilidades solicitada.

### Propiedad inmutable y archivado

Las instancias de red social registrarán su autor al crearse. Ese vínculo no admitirá actualización por ningún actor. Las instancias de variable no almacenarán autor: su propiedad y permisos derivarán exclusivamente de la instancia de red social padre. El propietario de la instancia de red podrá actualizar únicamente los datos funcionales de las instancias activas y archivarlas en vez de borrarlas. El archivado preservará el registro para auditoría, bloqueará cambios posteriores y excluirá la instancia de toda presentación pública.

Se descarta el borrado físico porque elimina la trazabilidad de quién creó una instancia de red y de sus valores publicados. Se descarta un autor duplicado en instancias de variables porque su propiedad queda determinada de forma inequívoca por la instancia de red padre.

### Rutas y foto externa

La aplicación aportará una ruta autenticada bajo `/dashboard/profile/` para editar los datos propios y gestionar instancias de red y valores, y una ruta pública bajo `/profiles/<public_username>/`. La foto se representará mediante una `photo_url` opcional validada como URL externa. La presentación pública usará esa URL directamente y no almacenará ni procesará archivos de imagen.

Se descarta la subida de archivos porque requeriría definir almacenamiento, entrega de media y gestión de recursos. La validación comprobará la estructura de la URL, no la disponibilidad ni el contenido remoto de la imagen.

### Desarrollo guiado por pruebas

Cada capacidad se implementará con el ciclo red-green-refactor: primero una prueba que exprese el escenario del spec y falle, después la implementación mínima que la haga pasar y finalmente la simplificación sin cambiar comportamiento. Las tareas se agrupan por capacidad para evitar implementar primero todos los modelos y probarlos al final.

El plan de la rama padre conserva únicamente sus tareas aprobadas. Si una rama hija de implementación descubre una tarea nueva, la registrará como `+=<número>` en su seguimiento de ejecución, sin renumerar ni modificar el plan aprobado.

## Risks / Trade-offs

- [Una plantilla puede referenciar variables no asociadas y generar enlaces incompletos] → Validar las referencias de `template_url` contra `SocialNetworkConfig` al guardar la configuración y cubrirlo con pruebas de modelo y admin.
- [Cambiar el `regex` de una variable puede volver inválidos valores ya guardados] → Las reglas nuevas se aplican a escrituras futuras; el admin debe advertir que las modificaciones no reescriben los valores existentes.
- [Una instancia puede ser reasignada o eliminada y perder trazabilidad] → Hacer inmutable el autor y aplicar archivado sin borrado físico, con pruebas de propiedad y exclusión pública.
- [Una imagen externa puede no estar disponible o cambiar fuera del sistema] → Validar la estructura de `photo_url` y omitir la imagen en la presentación cuando la carga del navegador falle.
- [Un usuario sin perfil podría recibir una respuesta no encontrada en su URL pública] → La vista pública manejará la ausencia del perfil sin exponer información privada del usuario.

## Migration Plan

1. Añadir la aplicación y los modelos con sus restricciones y relaciones.
2. Generar y aplicar las migraciones antes de habilitar las rutas de edición y consulta.
3. Registrar las definiciones en Django admin y desplegar las vistas, formularios y plantillas.
4. Verificar permisos, configuración, valores, nombre público y publicación mediante pruebas de Django y `manage.py check`.
5. Si se requiere reversión, retirar rutas y admin, y revertir la migración de la aplicación; los archivos media existentes podrán limpiarse por separado al no afectar datos de autenticación.
