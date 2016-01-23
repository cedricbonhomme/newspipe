var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var MenuActionTypes = require('../constants/JarrConstants').MenuActionTypes;
var EventEmitter = require('events').EventEmitter;
var CHANGE_EVENT = 'change_menu';
var assign = require('object-assign');


var MenuStore = assign({}, EventEmitter.prototype, {
    _datas: {filter: 'all', categories: [], active_type: null, active_id: null,
             all_unread_count: 0, feed_in_error: false},
    getAll: function() {
        return this._datas;
    },
    setFilter: function(value) {
        if(this._datas.filter != value) {
            this._datas.filter = value;
            this.emitChange();
        }
    },
    setActive: function(type, value) {
        if(this._datas.active_id != value || this._datas.active_type != type) {
            this._datas.active_type = type;
            this._datas.active_id = value;
            this.emitChange();
        }
    },
    readFeedArticle: function(feed_id) {
        // TODO
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


MenuStore.dispatchToken = JarrDispatcher.register(function(action) {
    switch(action.type) {
        case MenuActionTypes.RELOAD_MENU:
            MenuStore._datas['categories'] = action.categories;
            MenuStore._datas['feed_in_error'] = action.feed_in_error;
            MenuStore._datas['all_unread_count'] = action.all_unread_count;
            MenuStore.emitChange();
            break;
        case MenuActionTypes.PARENT_FILTER:
            MenuStore.setActive(action.filter_type, action.filter_id);
            break;
        case MenuActionTypes.MENU_FILTER:
            MenuStore.setFilter(action.filter);
            break;
        case MenuActionTypes.MENU_FILTER:
            MenuStore.setFilter(action.filter);
            break;
        case MenuActionTypes.MENU_FILTER:
            MenuStore.setFilter(action.filter);
            break;

        default:
            // do nothing
    }
});

module.exports = MenuStore;
