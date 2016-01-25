var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var jquery = require('jquery');
var RightPanelStore = require('../stores/RightPanelStore');


var RightPanelActions = {
    load: function(obj_type, obj_id) {
        filters = MiddlePanelStore.getRequestFilter();
        jquery.getJSON('api/v2.0/' + obj_type + '/' + obj_id, function(payload) {
            _last_fetched_with = filters;
            JarrDispatcher.dispatch({
                type: ActionTypes.LOAD_RIGHT_PANEL,
                articles: payload.articles,
            });
        });
    },
};

module.exports = RightPanelActions;
