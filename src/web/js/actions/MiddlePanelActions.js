var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var MiddlePanelActionTypes = require('../constants/JarrConstants').MiddlePanelActionTypes;


var MiddlePanelActions = {
    reload: function() {
        $.getJSON('/middle_panel', function(payload) {
            JarrDispatcher.dispatch({
                type: MiddlePanelActionTypes.RELOAD_MIDDLE_PANEL,
                articles: payload.articles,
            });
        });
    },
    removeParentFilter: function(parent_type, parent_id) {
        JarrDispatcher.dispatch({
            type: MiddlePanelActionTypes.MIDDLE_PANEL_PARENT_FILTER,
            parent_type: null,
            parent_id: null,
        });
    },
    setCategoryFilter: function(category_id) {
        JarrDispatcher.dispatch({
            type: MiddlePanelActionTypes.MIDDLE_PANEL_PARENT_FILTER,
            parent_type: 'category',
            parent_id: category_id,
        });
    },
    setFeedFilter: function(feed_id) {
        JarrDispatcher.dispatch({
            type: MiddlePanelActionTypes.MIDDLE_PANEL_PARENT_FILTER,
            parent_type: 'feed',
            parent_id: feed_id,
        });
    },
    setFilterMiddlePanelAll: function() {
        JarrDispatcher.dispatch({
            component: 'middle_panel',
            type: MiddlePanelActionTypes.MIDDLE_PANEL_FILTER_ALL,
        });
    },
    setFilterMiddlePanelUnread: function() {
        JarrDispatcher.dispatch({
            component: 'middle_panel',
            type: MiddlePanelActionTypes.MIDDLE_PANEL_FILTER_UNREAD,
        });
    },
    setFilterMiddlePanelUnread: function() {
        JarrDispatcher.dispatch({
            type: MiddlePanelActionTypes.MIDDLE_PANEL_FILTER_LIKED,
        });
    },
};

module.exports = MiddlePanelActions;
