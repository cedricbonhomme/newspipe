var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
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
        case ActionTypes.RELOAD_MENU:
            MenuStore._datas['categories'] = action.categories;
            MenuStore._datas['feed_in_error'] = action.feed_in_error;
            MenuStore._datas['all_unread_count'] = action.all_unread_count;
            MenuStore.emitChange();
            break;
        case ActionTypes.PARENT_FILTER:
            MenuStore.setActive(action.filter_type, action.filter_id);
            break;
        case ActionTypes.MENU_FILTER:
            MenuStore.setFilter(action.filter);
            break;
        case ActionTypes.MENU_FILTER:
            MenuStore.setFilter(action.filter);
            break;
        case ActionTypes.MENU_FILTER:
            MenuStore.setFilter(action.filter);
            break;
        case ActionTypes.CHANGE_ATTR:
            if(action.attribute != 'read') {
                return;
            }
            var val = action.value_num;
            action.articles.map(function(article) {
                for(var i in MenuStore._datas.categories) {
                    if(MenuStore._datas.categories[i].id == article.category_id) {
                        for(var j in MenuStore._datas.categories[i].feeds) {
                            if(MenuStore._datas.categories[i].feeds[j].id == article.feed_id) {
                                MenuStore._datas.categories[i].feeds[j].unread += val;
                                break;

                            }
                        }
                        MenuStore._datas.categories[i].unread += val;
                        break;
                    }
                }
            });
            MenuStore.emitChange();
            break;
        default:
            // do nothing
    }
});

module.exports = MenuStore;
