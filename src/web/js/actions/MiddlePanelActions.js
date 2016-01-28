var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var jquery = require('jquery');
var MiddlePanelStore = require('../stores/MiddlePanelStore');

var _last_fetched_with = {};
var shouldFetch = function(filters) {
    return true;  // FIXME disabling intelligent fetch for now, no caching better that bad one
//    if(filters.filter != null // undefined means unchanged
//            && (_last_fetched_with.filter != 'all'
//                || _last_fetched_with.filter != filters.filter)) {
//        return true;
//    }
//    if(_last_fetched_with.filter_type != null) {
//        if(_last_fetched_with.filter_type != filters.filter_type) {
//            return true;
//        }
//        if(_last_fetched_with.filter_id != filters.filter_id) {
//            return true;
//        }
//    }
//    return false;
}
var key_whitelist = ['filter_id', 'filter_type',
                     'query', 'search_title', 'search_content'];
var reloadIfNecessaryAndDispatch = function(dispath_payload) {
    if(shouldFetch(dispath_payload)) {
        var filters = MiddlePanelStore.getRequestFilter();
        key_whitelist.map(function(key) {
            if(key in dispath_payload) {
                filters[key] = dispath_payload[key];
            }
        });
        jquery.getJSON('/middle_panel', filters,
                function(payload) {
                    dispath_payload.articles = payload.articles;
                    JarrDispatcher.dispatch(dispath_payload);
                    _last_fetched_with = MiddlePanelStore.getRequestFilter();
        });
    } else {
        JarrDispatcher.dispatch(dispath_payload);
    }
}


var MiddlePanelActions = {
    reload: function() {
        reloadIfNecessaryAndDispatch({
            type: ActionTypes.RELOAD_MIDDLE_PANEL,
        });
    },
    search: function(search) {
        MiddlePanelStore._datas.display_search = true;
        MiddlePanelStore._datas.query = search.query;
        MiddlePanelStore._datas.search_content = search.content;
        MiddlePanelStore._datas.search_content = search.content;
        this.reload();
    },
    search_off: function() {
        MiddlePanelStore._datas.display_search = false;
        this.reload();
    },
    removeParentFilter: function() {
        reloadIfNecessaryAndDispatch({
            type: ActionTypes.PARENT_FILTER,
            filter_type: null,
            filter_id: null,
        });
    },
    setCategoryFilter: function(category_id) {
        reloadIfNecessaryAndDispatch({
            type: ActionTypes.PARENT_FILTER,
            filter_type: 'category_id',
            filter_id: category_id,
        });
    },
    setFeedFilter: function(feed_id) {
        reloadIfNecessaryAndDispatch({
            type: ActionTypes.PARENT_FILTER,
            filter_type: 'feed_id',
            filter_id: feed_id,
        });
    },
    setFilter: function(filter) {
        reloadIfNecessaryAndDispatch({
            type: ActionTypes.MIDDLE_PANEL_FILTER,
            filter: filter,
        });
    },
    changeRead: function(category_id, feed_id, article_id, new_value){
        jquery.ajax({type: 'PUT',
                contentType: 'application/json',
                data: JSON.stringify({readed: new_value}),
                url: "api/v2.0/article/" + article_id,
                success: function () {
                    JarrDispatcher.dispatch({
                        type: ActionTypes.CHANGE_ATTR,
                        attribute: 'read',
                        value_bool: new_value,
                        value_num: new_value ? -1 : 1,
                        articles: [{article_id: article_id,
                                    category_id: category_id,
                                    feed_id: feed_id}],
                    });
                },
        });
    },
    changeLike: function(category_id, feed_id, article_id, new_value){
        jquery.ajax({type: 'PUT',
                contentType: 'application/json',
                data: JSON.stringify({like: new_value}),
                url: "api/v2.0/article/" + article_id,
                success: function () {
                    JarrDispatcher.dispatch({
                        type: ActionTypes.CHANGE_ATTR,
                        attribute: 'liked',
                        value_bool: new_value,
                        value_num: new_value ? -1 : 1,
                        articles: [{article_id: article_id,
                                    category_id: category_id,
                                    feed_id: feed_id}],
                    });
                },
        });
    },
    markAllAsRead: function() {
        var filters = MiddlePanelStore.getRequestFilter();
        jquery.ajax({type: 'PUT',
                contentType: 'application/json',
                data: JSON.stringify(filters),
                url: "/mark_all_as_read",
                success: function (payload) {
                    JarrDispatcher.dispatch({
                        type: ActionTypes.CHANGE_ATTR,
                        attribute: 'read',
                        value_num: -1,
                        value_bool: true,
                        articles: payload.articles,
                    });
                },
        });
    },
};

module.exports = MiddlePanelActions;
