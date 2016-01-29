var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var jquery = require('jquery');

var RightPanelActions = {
    loadArticle: function(article_id) {
        jquery.getJSON('/getart/' + article_id,
            function(payload) {
                JarrDispatcher.dispatch({
                    type: ActionTypes.LOAD_ARTICLE,
                    article: payload,
                });
            }
        );

    },
};

module.exports = RightPanelActions;
