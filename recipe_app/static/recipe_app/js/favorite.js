const favoriteButton = document.getElementById('favorite-button');

let isFavorite = false;

favoriteButton.addEventListener('click', function () {
    isFavorite = !isFavorite;
    if (isFavorite) {
        favoriteButton.querySelector('svg').setAttribute('fill', 'red');

        // お気に入りに追加する処理を追加することもできます
        console.log('Added to favorites');

    } else {
        favoriteButton.querySelector('svg').setAttribute('fill', 'none');

        // お気に入りから削除する処理を追加することもできます
        console.log('Removed from favorites');
    }
});