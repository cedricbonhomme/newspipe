/*
 * Copyright (c) 2014-2015, Facebook, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 *
 * TodoConstants
 */

var keyMirror = require('keymirror');

module.exports = {
    MenuActionTypes: keyMirror({
        RELOAD_MENU: null,
        PARENT_FILTER: null,
        MENU_FILTER: null,
    }),
    MiddlePanelActionTypes: keyMirror({
        PARENT_FILTER: null,
        RELOAD_MIDDLE_PANEL: null,
        MIDDLE_PANEL_FILTER: null,
        CHANGE_ATTR: null,
    }),
    RightPanelActionTypes: keyMirror({
        LOAD_RIGHT_PANEL: null,
    }),
};
