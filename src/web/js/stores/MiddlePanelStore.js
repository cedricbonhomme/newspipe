var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var MiddlePanelActionTypes = require('../constants/JarrConstants').MiddlePanelActionTypes;
var EventEmitter = require('events').EventEmitter;
var CHANGE_EVENT = 'change_middle_panel';
var assign = require('object-assign');


var MiddlePanelStore = assign({}, EventEmitter.prototype, {
    _datas: {filter: 'unread', articles: [],
             parent_filter_type: null, parent_filter_id: null},
    getAll: function() {
        return this._datas;
    },
    getArticles: function() {
        var articles = [];
        var key = null;
        var id = null;
        if (this._datas.parent_filter_type) {
            key = this._datas.parent_filter_type + '_id';
            id = this._datas.parent_filter_id;
        }
        this._datas.articles.map(function(article) {
            if(!key || article[key] == id) {
                articles.push(article);
            }
        });
        return articles;
    },
    setFilter: function(value) {
        if(this._datas.filter != value) {
            this._datas.filter = value;
            this.emitChange();
        }
    },
    setParentFilter: function(type, value) {
        if(this._datas['parent_filter_id'] != value
                || this._datas['parent_filter_type'] != type) {
            this._datas['parent_filter_type'] = type;
            this._datas['parent_filter_id'] = value;
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


MiddlePanelStore.dispatchToken = JarrDispatcher.register(function(action) {
    switch(action.type) {
        case MiddlePanelActionTypes.RELOAD_MIDDLE_PANEL:
            MiddlePanelStore._datas['articles'] = action.articles;
            MiddlePanelStore.emitChange();
            break;
        // PARENT FILTER
        case MiddlePanelActionTypes.MIDDLE_PANEL_PARENT_FILTER:
            MiddlePanelStore.setParentFilter(action.parent_type,
                                             action.parent_id);
            break;
        // FILTER
        case MiddlePanelActionTypes.MIDDLE_PANEL_FILTER_ALL:
            MiddlePanelStore.setFilter('all');
            break;
        case MiddlePanelActionTypes.MIDDLE_PANEL_FILTER_UNREAD:
            MiddlePanelStore.setFilter('unread');
            break;
        case MiddlePanelActionTypes.MIDDLE_PANEL_FILTER_LIKED:
            MiddlePanelStore.setFilter('liked');
            break;


        default:
            // do nothing
    }
});

module.exports = MiddlePanelStore;
