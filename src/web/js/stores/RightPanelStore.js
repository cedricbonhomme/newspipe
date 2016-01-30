var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var EventEmitter = require('events').EventEmitter;
var CHANGE_EVENT = 'change_middle_panel';
var assign = require('object-assign');
var MenuStore = require('../stores/MenuStore');


var RightPanelStore = assign({}, EventEmitter.prototype, {
    category: null,
    feed: null,
    article: null,
    current: null,
    getAll: function() {
        return {category: this.category, feed: this.feed,
                article: this.article, current: this.current};
    },
    emitChange: function() {
        this.emit(CHANGE_EVENT);
    },
    addChangeListener: function(callback) {
        this.on(CHANGE_EVENT, callback);
    },
    removeChangeListener: function(callback) {
        this.removeListener(CHANGE_EVENT, callback);
    },
});


RightPanelStore.dispatchToken = JarrDispatcher.register(function(action) {
    switch(action.type) {
        case ActionTypes.PARENT_FILTER:
            RightPanelStore.article = null;
            if(action.filter_id == null) {
                RightPanelStore.category = null;
                RightPanelStore.feed = null;
                RightPanelStore.current = null;
            } else if(action.filter_type == 'category_id') {
                RightPanelStore.category = MenuStore._datas.categories[action.filter_id];
                RightPanelStore.feed = null;
                RightPanelStore.current = 'category';
                RightPanelStore.emitChange();
            } else {

                RightPanelStore.feed = MenuStore._datas.feeds[action.filter_id];
                RightPanelStore.category = MenuStore._datas.categories[RightPanelStore.feed.category_id];
                RightPanelStore.current = 'feed';
                RightPanelStore.emitChange();
            }
            break;
        case ActionTypes.LOAD_ARTICLE:
            RightPanelStore.feed = MenuStore._datas.feeds[action.article.feed_id];
            RightPanelStore.category = MenuStore._datas.categories[action.article.category_id];
            RightPanelStore.article = action.article;
            RightPanelStore.current = 'article';
            RightPanelStore.emitChange();
            break;
        case ActionTypes.RELOAD_MENU:
            RightPanelStore.article = null;
            if(RightPanelStore.category && !(RightPanelStore.category.id.toString() in action.categories)) {
                RightPanelStore.category = null;
                RightPanelStore.current = null;
            }
            if(RightPanelStore.feed && !(RightPanelStore.feed.id.toString() in action.feeds)) {
                RightPanelStore.feed = null;
                RightPanelStore.current = null;
            }
            if(RightPanelStore.current == 'article') {
                RightPanelStore.current = null;
            }
            RightPanelStore.emitChange();
        default:
            // pass
    }
});

module.exports = RightPanelStore;
