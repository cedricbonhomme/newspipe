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
                feed_in_error: payload.feed_in_error,
                all_unread_count: payload.all_unread_count,
            });
        });
    },
    setFilterAll: function() {
        JarrDispatcher.dispatch({
            type: MenuActionTypes.MENU_FILTER,
            filter: 'all',
        });
    },
    setFilterUnread: function() {
        JarrDispatcher.dispatch({
            type: MenuActionTypes.MENU_FILTER,
            filter: 'unread',
        });
    },
    setFilterError: function() {
        JarrDispatcher.dispatch({
            type: MenuActionTypes.MENU_FILTER,
            filter: 'error',
        });
    },

};

module.exports = MenuActions;
