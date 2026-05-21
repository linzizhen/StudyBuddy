/**
 * StudyPal 路由系统 v2.0
 * 基于 Hash 的客户端路由，支持页面切换和参数传递
 */

class Router {
    constructor() {
        this.routes = new Map();
        this.currentPage = null;
        this.currentParams = [];
        this._init();
    }

    /**
     * 注册路由
     * @param {string} name - 路由名称
     * @param {Function} handler - 路由处理器
     */
    register(name, handler) {
        this.routes.set(name, handler);
    }

    /**
     * 初始化路由监听
     */
    _init() {
        window.addEventListener('hashchange', () => this._handleRoute());
        window.addEventListener('load', () => this._handleRoute());
    }

    /**
     * 处理路由变化
     */
    _handleRoute() {
        const hash = window.location.hash.slice(1) || 'home';
        const [page, ...params] = hash.split('/');

        if (this.routes.has(page)) {
            this.navigate(page, params);
        } else {
            this.navigate('home', []);
        }
    }

    /**
     * 导航到指定页面
     * @param {string} page - 页面名称
     * @param {Array} params - 路由参数
     */
    navigate(page, params = []) {
        if (!this.routes.has(page)) {
            console.warn(`Route "${page}" not found`);
            return;
        }

        // 清理旧页面
        if (this.currentPage && this.routes.get(this.currentPage)?.unmount) {
            this.routes.get(this.currentPage).unmount();
        }

        // 加载新页面
        this.currentPage = page;
        this.currentParams = params;

        const handler = this.routes.get(page);
        handler.mount(params);

        // 更新导航状态
        this._updateNavigation(page);

        // 更新浏览器历史
        window.location.hash = params.length > 0 ? `${page}/${params.join('/')}` : page;
    }

    /**
     * 更新底部导航状态
     */
    _updateNavigation(page) {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.page === page);
        });

        // 同步更新 State
        if (window.State) {
            State.set('ui.currentPage', page);
        }
    }

    /**
     * 获取当前页面名称
     */
    getCurrentPage() {
        return this.currentPage;
    }

    /**
     * 获取当前路由参数
     */
    getParams() {
        return this.currentParams;
    }

    /**
     * 返回首页
     */
    goHome() {
        this.navigate('home');
    }

    /**
     * 刷新当前页面
     */
    refresh() {
        if (this.currentPage) {
            this.navigate(this.currentPage, this.currentParams);
        }
    }
}

const router = new Router();

// 导出
window.Router = Router;
window.router = router;
