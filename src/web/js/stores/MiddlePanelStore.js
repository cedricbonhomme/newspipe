var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var ActionTypes = require('../constants/JarrConstants');
var EventEmitter = require('events').EventEmitter;
var CHANGE_EVENT = 'change_middle_panel';
var assign = require('object-assign');


var MiddlePanelStore = assign({}, EventEmitter.prototype, {
    filter_whitelist: ['filter', 'filter_id', 'filter_type', 'display_search',
                       'query', 'search_title', 'search_content'],
    _datas: {articles: [], selected_article: null,
             filter: 'unread', filter_type: null, filter_id: null,
             display_search: false, query: null,
             search_title: true, search_content: false},
    getAll: function() {
        return this._datas;
    },
    getRequestFilter: function(display_search) {
        var filters = {'filter': this._datas.filter,
                       'filter_type': this._datas.filter_type,
                       'filter_id': this._datas.filter_id,
        };
        if(display_search || (display_search == undefined && this._datas.display_search)) {
            filters.query = this._datas.query;
            filters.search_title = this._datas.search_title;
            filters.search_content = this._datas.search_content;
        };
        return filters;
    },
    getArticles: function() {
        var key = null;
        var id = null;
        if (this._datas.filter_type) {
            key = this._datas.filter_type;
            id = this._datas.filter_id;
        }
        return this._datas.articles
        .map(function(article) {
            if(article.article_id == this._datas.selected_article) {
                article.selected = true;
            } else if(article.selected) {
                article.selected = false;
            }
            return article;
        }.bind(this))
        .filter(function(article) {
            return (article.selected || ((!key || article[key] == id)
                    && (this._datas.filter == 'all'
                        || (this._datas.filter == 'unread' && !article.read)
                        || (this._datas.filter == 'liked' && article.liked))));
        }.bind(this));

    },
    setArticles: function(articles) {
        if(articles || articles == []) {
            this._datas.articles = articles;
            return true;
        }
        return false;
    },
    registerFilter: function(action) {
        var changed = false;
        this.filter_whitelist.map(function(key) {
            if(key in action && this._datas[key] != action[key]) {
                changed = true;
                this._datas[key] = action[key];
            }
        }.bind(this));
        return changed;
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
    if (action.type == ActionTypes.RELOAD_MIDDLE_PANEL
            || action.type == ActionTypes.PARENT_FILTER
            || action.type == ActionTypes.MIDDLE_PANEL_FILTER) {
        changed = MiddlePanelStore.registerFilter(action);
        changed = MiddlePanelStore.setArticles(action.articles) || changed;
    } else if (action.type == ActionTypes.MARK_ALL_AS_READ) {
        changed = MiddlePanelStore.registerFilter(action);
        for(var i in action.articles) {
            action.articles[i].read = true;
        }
        changed = MiddlePanelStore.setArticles(action.articles) || changed;
    } else if (action.type == ActionTypes.CHANGE_ATTR) {
            var attr = action.attribute;
            var val = action.value_bool;
            action.articles.map(function(article) {
                for (var i in MiddlePanelStore._datas.articles) {
                    if(MiddlePanelStore._datas.articles[i].article_id == article.article_id) {
                        if (MiddlePanelStore._datas.articles[i][attr] != val) {
                            MiddlePanelStore._datas.articles[i][attr] = val;
                            // avoiding redraw if not filter, display won't change anyway
                            if(MiddlePanelStore._datas.filter != 'all') {
                                changed = true;
                            }
                        }
                        break;
                    }
                }
            });
    } else if (action.type == ActionTypes.LOAD_ARTICLE) {
        changed = true;
        MiddlePanelStore._datas.selected_article = action.article.id;
        for (var i in MiddlePanelStore._datas.articles) {
            if(MiddlePanelStore._datas.articles[i].article_id == action.article.id) {
                MiddlePanelStore._datas.articles[i].read = true;
                break;
            }
        }
    }
    if(changed) {MiddlePanelStore.emitChange();}
});

module.exports = MiddlePanelStore;
