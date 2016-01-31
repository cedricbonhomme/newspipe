var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var jquery = require('jquery');


var MenuActions = {
    // PARENT FILTERS
    reload: function() {
        jquery.getJSON('/menu', function(payload) {
            JarrDispatcher.dispatch({
                type: ActionTypes.RELOAD_MENU,
                feeds: payload.feeds,
                categories: payload.categories,
                categories_order: payload.categories_order,
                is_admin: payload.is_admin,
                max_error: payload.max_error,
                error_threshold: payload.error_threshold,
                crawling_method: payload.crawling_method,
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
