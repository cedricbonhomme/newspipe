var keyMirror = require('keymirror');

module.exports = keyMirror({
        TOGGLE_MENU_FOLD: null,
        RELOAD_MENU: null,
        PARENT_FILTER: null,  // set a feed or a category as filter in menu
        MENU_FILTER: null,  // change displayed feed in the menu
        CHANGE_ATTR: null,  // edit an attr on an article (like / read)
        RELOAD_MIDDLE_PANEL: null,
        MIDDLE_PANEL_FILTER: null,  // set a filter (read/like/all)
        LOAD_ARTICLE: null,  // load a single article in right panel
        MARK_ALL_AS_READ: null,
});
