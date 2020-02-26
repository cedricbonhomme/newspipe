var jquery = require('jquery');
var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var MenuActions = require('../actions/MenuActions');

var RightPanelActions = {
    loadArticle: function(article_id, was_read_before, to_parse) {
        var suffix = '';
        if(to_parse) {
            suffix = '/parse';
        }
        jquery.getJSON('/getart/' + article_id + suffix,
            function(payload) {
                JarrDispatcher.dispatch({
                    type: ActionTypes.LOAD_ARTICLE,
                    article: payload,
                    was_read_before: was_read_before,
                });
            }
        );
    },
    _apiReq: function(meth, id, obj_type, data, success_callback) {
        var args = {type: meth, contentType: 'application/json',
                    url: "api/v2.0/" + obj_type + "/" + id}
        if(data) {args.data = JSON.stringify(data);}
        if(success_callback) {args.success = success_callback;}
        jquery.ajax(args);
    },
    putObj: function(id, obj_type, fields) {
        this._apiReq('PUT', id, obj_type, fields, MenuActions.reload);
    },
    delObj: function(id, obj_type, fields) {
        this._apiReq('DELETE', id, obj_type, null, MenuActions.reload);
    },
    resetErrors: function(feed_id) {
        this._apiReq('PUT', feed_id, 'feed', {error_count: 0, last_error: ''},
                     MenuActions.reload);

    },
};

module.exports = RightPanelActions;
