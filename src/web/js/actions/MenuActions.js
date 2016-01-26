var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var jquery = require('jquery');


var MenuActions = {
    // PARENT FILTERS
    reload: function() {
        jquery.getJSON('/menu', function(payload) {
            JarrDispatcher.dispatch({
                type: ActionTypes.RELOAD_MENU,
                categories: payload.categories,
                feed_in_error: payload.feed_in_error,
                all_unread_count: payload.all_unread_count,
            });
        });
    },
    setFilter: function(filter) {
        JarrDispatcher.dispatch({
            type: ActionTypes.MENU_FILTER,
            filter: filter,
        });
    },
};

module.exports = MenuActions;
