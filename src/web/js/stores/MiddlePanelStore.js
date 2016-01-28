var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var EventEmitter = require('events').EventEmitter;
var CHANGE_EVENT = 'change_middle_panel';
var assign = require('object-assign');


var MiddlePanelStore = assign({}, EventEmitter.prototype, {
    _datas: {filter: 'unread', articles: [],
             filter_type: null, filter_id: null,
             display_search: false, query: null,
             search_title: true, search_content: false},
    getAll: function() {
        return this._datas;
    },
    getRequestFilter: function() {
        var filters = {'filter': this._datas.filter,
                       'filter_type': this._datas.filter_type,
                       'filter_id': this._datas.filter_id,
        };
        if(this._datas.display_search) {
            filters.query = this._datas.query;
            filters.search_title = this._datas.search_title;
            filters.search_content = this._datas.search_content;
        };
        return filters;
    },
    getArticles: function() {
        var key = null;
        var id = null;
        var filter = this._datas.filter;
        if (this._datas.filter_type) {
            key = this._datas.filter_type;
            id = this._datas.filter_id;
        }
        return this._datas.articles.filter(function(article) {
            return ((!key || article[key] == id)
                    && (filter == 'all'
                        || (filter == 'unread' && !article.read)
                        || (filter == 'liked' && article.liked)));
        });
    },
    setArticles: function(articles) {
        if(articles || articles == []) {
            this._datas.articles = articles;
            return true;
        }
        return false;
    },
    setFilter: function(value) {
        if(this._datas.filter != value) {
            this._datas.filter = value;
            return true;
        }
        return false;
    },
    setParentFilter: function(type, value) {
        if(this._datas.filter_id != value || this._datas.filter_type != type) {
            this._datas.filter_type = type;
            this._datas.filter_id = value;
            return true;
        }
        return false;
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


MiddlePanelStore.dispatchToken = JarrDispatcher.register(function(action) {
    var changed = false;
    switch(action.type) {
        case ActionTypes.RELOAD_MIDDLE_PANEL:
            MiddlePanelStore.setArticles(action.articles);
            MiddlePanelStore.emitChange();
            break;
        case ActionTypes.PARENT_FILTER:
            changed = MiddlePanelStore.setParentFilter(action.filter_type,
                                                       action.filter_id);
            changed = MiddlePanelStore.setArticles(action.articles) || changed;
            if(changed) {MiddlePanelStore.emitChange();}
            break;
        case ActionTypes.MIDDLE_PANEL_FILTER:
            changed = MiddlePanelStore.setFilter(action.filter);
            changed = MiddlePanelStore.setArticles(action.articles) || changed;
            if(changed) {MiddlePanelStore.emitChange();}
            break;
        case ActionTypes.CHANGE_ATTR:
            var attr = action.attribute;
            var val = action.value_bool;
            action.articles.map(function(article) {
                for (var i in MiddlePanelStore._datas.articles) {
                    if(MiddlePanelStore._datas.articles[i].article_id == article.article_id) {
                        if (MiddlePanelStore._datas.articles[i][attr] != val) {
                            MiddlePanelStore._datas.articles[i][attr] = val;
                            // avoiding redraw if not filter, display won't change anyway
                            if(MiddlePanelStore._datas.filter != 'all') {
                                MiddlePanelStore.emitChange();
                            }
                        }
                        break;
                    }
                }
            });
            break;
        default:
            // pass
    }
});

module.exports = MiddlePanelStore;
