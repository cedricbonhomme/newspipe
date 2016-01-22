var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var MenuActionTypes = require('../constants/JarrConstants').MenuActionTypes;
var jquery = require('jquery');


var MenuActions = {
    // PARENT FILTERS
    reload: function() {
        jquery.getJSON('/menu', function(payload) {
            JarrDispatcher.dispatch({
                type: MenuActionTypes.RELOAD_MENU,
                categories: payload.categories,
                all_unread_count: payload.all_unread_count,
            });
        });
    },
    setFilterAll: function() {
        JarrDispatcher.dispatch({
            component: 'menu',
            type: MenuActionTypes.MENU_FILTER_ALL,
        });
    },
    setFilterUnread: function() {
        JarrDispatcher.dispatch({
            component: 'menu',
            type: MenuActionTypes.MENU_FILTER_UNREAD,
        });
    },
    setFilterError: function() {
        JarrDispatcher.dispatch({
            type: MenuActionTypes.MENU_FILTER_ERROR,
        });
    },

};

module.exports = MenuActions;
