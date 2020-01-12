# Permissions

To perform actions, users need permissions that allow them to do so.

Squirrel has some default permissions for all models:

* view
* add
* change
* delete

Those permissions apply to the frontend and the [API](03-api.md) as well.

## Orders

Orders have some special behavior that allows for team management: Users implicitly gain the `view` permission for
**all orders of all teams they belong to**. 