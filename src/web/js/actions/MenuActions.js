var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var MenuActionTypes = require('../constants/JarrConstants').MenuActionTypes;


var MenuActions = {
    // PARENT FILTERS
    reload: function() {
        $.getJSON('/menu', function(payload) {
            JarrDispatcher.dispatch({
                type: MenuActionTypes.RELOAD_MENU,
                categories: payload.categories,
                all_unread_count: payload.all_unread_count,
            });
        });
    },
    setFilterMenuAll: function() {
        JarrDispatcher.dispatch({
            component: 'menu',
            type: MenuActionTypes.MENU_FILTER_ALL,
        });
    },
    setFilterMenuUnread: function() {
        JarrDispatcher.dispatch({
            component: 'menu',
            type: MenuActionTypes.MENU_FILTER_UNREAD,
        });
    },
    setFilterMenuError: function() {
        JarrDispatcher.dispatch({
            type: MenuActionTypes.MENU_FILTER_ERROR,
        });
    },

};

module.exports = MenuActions;
