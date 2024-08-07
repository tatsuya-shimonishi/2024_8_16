document.addEventListener('DOMContentLoaded', () => {
    let isFavorite = [];

    // metaタグからCSRFトークンを取得する関数
    const getCsrfToken = () => {
        const meta = document.querySelector('meta[name="csrf_token"]');
        return meta ? meta.getAttribute('content') : '';
    };

    // クリックイベント
    document.addEventListener('click', function (event) {
        // フォームなどのデフォルトクリックで起動しないように設定
        // event.preventDefault();

        // starクラスの親svgタグを取得
        const svg = event.target.closest('.star');

        if (svg) {
            const frameStar = svg.querySelector('#frame-star');
            const fillStar = svg.querySelector('#fill-star');
            const item_id = frameStar.getAttribute('data-item-id');
            const data = new URLSearchParams({
                "item_id": item_id
            });
            let url = "";

            // 各お気に入りボタンの切り替え
            if (item_id in isFavorite) {
                isFavorite[item_id] = !isFavorite[item_id];
            } else {
                isFavorite[item_id] = true
            }

            // お気に入り登録
            if (isFavorite[item_id]) {
                frameStar.setAttribute('hidden', '');
                fillStar.removeAttribute('hidden');
                url = "/recipe_app/add_favorite/";

            // お気に入り削除
            } else {
                frameStar.removeAttribute('hidden');
                fillStar.setAttribute('hidden', '');
                url = "/recipe_app/delete_favorite/";
            }

            // 非同期で登録/削除を行う
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCsrfToken()
                },
                body: data.toString()
            })
                .then(response => response.json())
                .then(data => {
                    console.log('Success:', data);
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        }
    });
});