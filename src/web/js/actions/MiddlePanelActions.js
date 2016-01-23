var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var MiddlePanelActionTypes = require('../constants/JarrConstants').MiddlePanelActionTypes;
var jquery = require('jquery');
var MiddlePanelStore = require('../stores/MiddlePanelStore');

var _last_fetched_with = {};
var shouldFetch = function(filters) {
    if(filters.filter != null // undefined means unchanged
            && (_last_fetched_with.filter != 'all'
                || _last_fetched_with.filter != filters.filter)) {
        return true;
    }
    if(_last_fetched_with.filter_type != null) {
        if(_last_fetched_with.filter_type != filters.filter_type) {
            return true;
        }
        if(_last_fetched_with.filter_id != filters.filter_id) {
            return true;
        }
    }
    return false;
}
var reloadIfNecessaryAndDispatch = function(dispath_payload) {
    if(shouldFetch(dispath_payload)) {
        filters = MiddlePanelStore.getRequestFilter();
        for (var key in filters) {
            if(dispath_payload[key] != null) {
                filters[key] = dispath_payload[key];
            }
        }
        jquery.getJSON('/middle_panel', dispath_payload, function(payload) {
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
        filters = MiddlePanelStore.getRequestFilter();
        jquery.getJSON('/middle_panel', filters, function(payload) {
            _last_fetched_with = filters;
            JarrDispatcher.dispatch({
                type: MiddlePanelActionTypes.RELOAD_MIDDLE_PANEL,
                articles: payload.articles,
            });
        });
    },
    removeParentFilter: function(filter_type, filter_id) {
        reloadIfNecessaryAndDispatch({
            type: MiddlePanelActionTypes.MIDDLE_PANEL_PARENT_FILTER,
            filter_type: null,
            filter_id: null,
        });
    },
    setCategoryFilter: function(category_id) {
        reloadIfNecessaryAndDispatch({
            type: MiddlePanelActionTypes.MIDDLE_PANEL_PARENT_FILTER,
            filter_type: 'category',
            filter_id: category_id,
        });
    },
    setFeedFilter: function(feed_id) {
        reloadIfNecessaryAndDispatch({
            type: MiddlePanelActionTypes.MIDDLE_PANEL_PARENT_FILTER,
            filter_type: 'feed',
            filter_id: feed_id,
        });
    },
    setFilterAll: function() {
        reloadIfNecessaryAndDispatch({
            type: MiddlePanelActionTypes.MIDDLE_PANEL_FILTER,
            filter: 'all',
        });
    },
    setFilterUnread: function() {
        reloadIfNecessaryAndDispatch({
            type: MiddlePanelActionTypes.MIDDLE_PANEL_FILTER,
            filter: 'unread',
        });
    },
    setFilterLiked: function() {
        reloadIfNecessaryAndDispatch({
            type: MiddlePanelActionTypes.MIDDLE_PANEL_FILTER,
            filter: 'liked',
        });
    },
};

module.exports = MiddlePanelActions;
