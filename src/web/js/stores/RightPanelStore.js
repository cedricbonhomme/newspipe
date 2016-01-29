var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var EventEmitter = require('events').EventEmitter;
var CHANGE_EVENT = 'change_middle_panel';
var assign = require('object-assign');
var MenuStore = require('../stores/MenuStore');


var RightPanelStore = assign({}, EventEmitter.prototype, {
    _datas: {category: null, feed: null, article: null},
    getAll: function() {
        return this._datas;
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
            RightPanelStore._datas.article = null;
            if(action.filter_id == null) {
                RightPanelStore._datas.category = null;
                RightPanelStore._datas.feed = null;
            } else if(action.filter_type == 'category_id') {
                RightPanelStore._datas.category = MenuStore._datas.categories[action.filter_id];
                RightPanelStore._datas.feed = null;
                RightPanelStore._datas.current = 'category';
            } else {

                RightPanelStore._datas.feed = MenuStore._datas.feeds[action.filter_id];
                RightPanelStore._datas.category = MenuStore._datas.categories[RightPanelStore._datas.feed.category_id];
                RightPanelStore._datas.current = 'feed';
            }
            RightPanelStore.emitChange();
            break;
        case ActionTypes.LOAD_ARTICLE:
            RightPanelStore._datas.feed = MenuStore._datas.feeds[action.article.feed_id];
            RightPanelStore._datas.category = MenuStore._datas.categories[action.article.category_id];
            RightPanelStore._datas.article = action.article;
            RightPanelStore._datas.current = 'article';
            RightPanelStore.emitChange();
            break;
        default:
            // pass
    }
});

module.exports = RightPanelStore;
