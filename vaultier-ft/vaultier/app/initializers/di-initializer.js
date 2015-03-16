import DALClient from 'vaultier/app/models/core/client';
import Errors from 'vaultier/app/services/errors';
import Session from 'vaultier/app/services/session/session';
import Storage from 'vaultier/app/services/session/storage';
import Auth from 'vaultier/app/services/auth/auth';
import Tree from 'vaultier/app/services/tree';
import Invitations from 'vaultier/app/services/invitations';
import Coder from 'vaultier/app/services/key/coder';
import KeyTransfer from 'vaultier/app/services/key/key-transfer';
import NodeKey from 'vaultier/app/services/key/node-key';
import NodeKeyMock from 'vaultier/app/mock/node-key-mock';
import ChangeKey from 'vaultier/app/services/key/change-key';
import NewUserInit from 'vaultier/app/services/new-user-init';
/* global ApplicationKernel, RL */

/**
 * Dependency injection initializer, service dependency injection should be defined here
 *
 * Uses standard ember initializer pattern: <a target="blank" href="http://emberjs.com/api/classes/Ember.Application.html#toc_initializers">see ember docs</a>
 *
 * @class Vaultier.initializers.DI
 */

export default {
    name: 'vaultier-di',
    after: 'vaultier-boot',

    initialize: function (container, app) {

        // service:store
        app.register('store:main', DALClient, {instantiate: false});
        app.inject('route', 'store', 'store:main');
        app.inject('controller', 'store', 'store:main');
        app.inject('controller', 'router', 'router:main');
        app.inject('component', 'store', 'store:main');
        //also there lazy loading does not work properly with ember initialize:
        //@todo: mess - get rid of following code
        RL.set('client', DALClient);

        // service:errors
        //app.register('service:errors', Errors);
        //app.inject('route', 'errors', 'service:errors');
        //app.inject('component', 'errors', 'service:errors');
        //app.inject('view', 'errors', 'service:errors');
        //
        //app.inject('service:errors', 'errorController', 'controller:ErrorGeneric');
        //app.inject('service:errors', 'router', 'router:main');
//    app.inject('controller', 'errors', 'service:errors');


        // service:session and service:storage
        app.register('service:session', Session);
        app.register('service:storage', Storage);

        // service:auth
        app.register('service:auth', Auth);
        app.inject('service:auth', 'coder', 'service:coder');
        app.inject('service:auth', 'store', 'store:main');
        app.inject('service:auth', 'router', 'router:main');
        app.inject('service:auth', 'session', 'service:session');
        app.inject('service:auth', 'storage', 'service:storage');

        app.register('service:tree', Tree);

        app.inject('route', 'auth', 'service:auth');
        app.inject('route', 'tree', 'service:tree');
        app.inject('controller', 'auth', 'service:auth');
        app.inject('controller', 'tree', 'service:tree');
        app.inject('service:tree', 'store', 'store:main');
        app.inject('service:tree', 'adapter', 'adapter:node');

        // service:coder
        app.register('service:coder', Coder);

        // service:invitations
        app.register('service:invitations', Invitations);
        app.inject('service:invitations', 'store', 'store:main');
        app.inject('service:invitations', 'session', 'service:session');
        app.inject('service:invitations', 'auth', 'service:auth');
        app.inject('service:invitations', 'router', 'router:main');
        app.inject('service:invitations', 'tree', 'service:tree');

        app.inject('route:InvitationUse', 'invitations', 'service:invitations');
        app.inject('route:InvitationAccept', 'invitations', 'service:invitations');
        app.inject('route', 'invitations', 'service:invitations');

        // service:keytransfer
        app.register('service:keytransfer', KeyTransfer);
        app.inject('service:keytransfer', 'store', 'store:main');
        app.inject('service:keytransfer', 'auth', 'service:auth');
        app.inject('service:keytransfer', 'coder', 'service:coder');

        // service:nodekey
        //if (ApplicationKernel.Config.environment !== 'dev-mock') {
            app.register('service:nodekey', NodeKeyMock);
        //} else {
        //  app.register('service:nodekey', NodeKey);
        //}
        app.inject('service:nodekey', 'auth', 'service:auth');
        app.inject('service:nodekey', 'store', 'store:main');
        app.inject('service:nodekey', 'coder', 'service:coder');
        app.inject('service:nodekey', 'keytransfer', 'service:keytransfer');

        // service:changekey
        app.register('service:changekey', ChangeKey);
        app.inject('route:SettingsKeys', 'changekey', 'service:changekey');
        app.inject('route:AuthLostKeyRecoveryRebuild', 'changekey', 'service:changekey');
        app.inject('service:changekey', 'store', 'store:main');
        app.inject('service:changekey', 'auth', 'service:auth');
        app.inject('service:changekey', 'coder', 'service:coder');

        // service:newuserinit
        app.register('service:newuserinit', NewUserInit);
        app.inject('service:newuserinit', 'auth', 'service:auth');
        app.inject('service:newuserinit', 'router', 'router:main');
        app.inject('service:newuserinit', 'invitations', 'service:invitations');
        app.inject('service:newuserinit', 'tree', 'service:tree');
        app.inject('service:newuserinit', 'store', 'store:main');
        app.inject('route:AuthRegisterCreds', 'newuserinit', 'service:newuserinit');


        // components injections
        app.inject('component:change-key', 'changekey', 'service:changekey');

        app.inject('component:roles-admin-box', 'auth', 'service:auth');
        // model injections - it is done in model inits

    }
};


