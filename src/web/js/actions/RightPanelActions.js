var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var jquery = require('jquery');

var RightPanelActions = {
    loadArticle: function(article_id, was_read_before) {
        jquery.getJSON('/getart/' + article_id,
            function(payload) {
                JarrDispatcher.dispatch({
                    type: ActionTypes.LOAD_ARTICLE,
                    article: payload,
                    was_read_before: was_read_before,
                });
            }
        );

    },
};

module.exports = RightPanelActions;
