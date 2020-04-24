# Permissions

To perform actions, users need permissions that allow them to do so.

Squirrel has some default permissions for all models:

* `view`
* `add`
* `change`
* `delete`

Those permissions apply to the frontend and the [API](03-api.md) as well.

## Orders

Orders have a second set of permissions that allow for specific actions to be performed for **all teams**.

Those are:

* `view_all_teams`
* `add_all_teams`
* `change_all_teams`
* `delete_all_teams`

This enables us to allow users to e.g. place orders for all teams without belonging to it which is a typical
helpdesk scenario.

**Those permissions do not implicitly grant the base permission.** If you want someone to be able to delete
orders for all teams, grant them the `delete` and the `delete_all_teams` permission. This was a carefully made decision
that follows the principle that *explicit is better than implicit.*