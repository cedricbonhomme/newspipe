var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var EventEmitter = require('events').EventEmitter;
var CHANGE_EVENT = 'change_menu';
var assign = require('object-assign');


var MenuStore = assign({}, EventEmitter.prototype, {
    _datas: {filter: 'all', feeds: {}, categories: {}, categories_order: [],
             active_type: null, active_id: null,
             is_admin: false, crawling_method: 'classic',
             all_unread_count: 0, max_error: 0, error_threshold: 0,
             all_folded: false},
    getAll: function() {
        return this._datas;
    },
    setFilter: function(value) {
        if(this._datas.filter != value) {
            this._datas.filter = value;
            this._datas.all_folded = null;
            this.emitChange();
        }
    },
    setActive: function(type, value) {
        if(this._datas.active_id != value || this._datas.active_type != type) {
            this._datas.active_type = type;
            this._datas.active_id = value;
            this._datas.all_folded = null;
            this.emitChange();
        }
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
            MenuStore._datas['feeds'] = action.feeds;
            MenuStore._datas['categories'] = action.categories;
            MenuStore._datas['categories_order'] = action.categories_order;
            MenuStore._datas['is_admin'] = action.is_admin;
            MenuStore._datas['max_error'] = action.max_error;
            MenuStore._datas['error_threshold'] = action.error_threshold;
            MenuStore._datas['crawling_method'] = action.crawling_method;
            MenuStore._datas['all_unread_count'] = action.all_unread_count;
            MenuStore._datas.all_folded = null;
            MenuStore.emitChange();
            break;
        case ActionTypes.PARENT_FILTER:
            MenuStore.setActive(action.filter_type, action.filter_id);
            if(action.filters && action.articles && !action.filters.query
                    && action.filters.filter == 'unread') {
                var new_unread = {};
                action.articles.map(function(article) {
                    if(!(article.feed_id in new_unread)) {
                        new_unread[article.feed_id] = 0;
                    }
                    if(!article.read) {
                        new_unread[article.feed_id] += 1;
                    }
                });
                var changed = false;
                for(var feed_id in new_unread) {
                    var old_unread = MenuStore._datas.feeds[feed_id].unread;
                    if(old_unread == new_unread[feed_id]) {
                        continue;
                    }
                    changed = true;
                    MenuStore._datas.feeds[feed_id].unread = new_unread[feed_id];
                    var cat_id = MenuStore._datas.feeds[feed_id].category_id;
                    MenuStore._datas.categories[cat_id].unread -= old_unread;
                    MenuStore._datas.categories[cat_id].unread += new_unread[feed_id];
                }
                if(changed) {
                    MenuStore._datas.all_folded = null;
                    MenuStore.emitChange();
                }
            }
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
                MenuStore._datas.categories[article.category_id].unread += val;
                MenuStore._datas.feeds[article.feed_id].unread += val;
            });
            MenuStore._datas.all_folded = null;
            MenuStore.emitChange();
            break;
        case ActionTypes.LOAD_ARTICLE:
            if(!action.was_read_before) {
                MenuStore._datas.categories[action.article.category_id].unread -= 1;
                MenuStore._datas.feeds[action.article.feed_id].unread -= 1;
                MenuStore._datas.all_folded = null;
                MenuStore.emitChange();
            }
            break;
        case ActionTypes.TOGGLE_MENU_FOLD:
            MenuStore._datas.all_folded = action.all_folded;
            MenuStore.emitChange();
            break;
        case ActionTypes.MARK_ALL_AS_READ:
            action.articles.map(function(art) {
                if(!art.read) {
                    MenuStore._datas.feeds[art.feed_id].unread -= 1;
                    if(art.category_id) {
                        MenuStore._datas.categories[art.category_id].unread -= 1;

                    }
                }
            });

            MenuStore._datas.all_folded = null;
            MenuStore.emitChange();
            break;
        default:
            // do nothing
    }
});

module.exports = MenuStore;
