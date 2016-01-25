var JarrDispatcher = require('../dispatcher/JarrDispatcher');
var RightPanelActionTypes = require('../constants/JarrConstants').RightPanelActionTypes;
var MenuActionTypes = require('../constants/JarrConstants').MenuActionTypes;
var EventEmitter = require('events').EventEmitter;
var CHANGE_EVENT = 'change_middle_panel';
var assign = require('object-assign');


var RightPanelStore = assign({}, EventEmitter.prototype, {
    _datas: {},
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
        default:
            // pass
    }
});

module.exports = RightPanelStore;
