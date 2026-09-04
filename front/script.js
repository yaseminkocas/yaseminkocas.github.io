/*
 * IMPORTANT:
 *
 * Replace this with the URL Render gives you after
 * deploying the backend.
 *
 * Example:
 *
 * const API_URL = "https://my-playlist-sync.onrender.com";
 */

const API_URL = "https://yaseminkocas-github-io.onrender.com";


async function syncPlaylist() {

    const button = document.getElementById("syncButton");
    const loading = document.getElementById("loading");
    const status = document.getElementById("status");
    const results = document.getElementById("results");

    button.disabled = true;
    loading.classList.remove("hidden");

    status.textContent = "Checking playlist...";
    results.innerHTML = "";

    try {

        const response = await fetch(`${API_URL}/sync`, {
            method: "POST"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Sync failed.");
        }

        if (data.new_files.length === 0) {

            status.textContent = "Playlist is already up to date.";

        } else {

            status.textContent =
                `${data.new_files.length} new song(s) found.`;

            for (const file of data.new_files) {

                const row = document.createElement("div");
                row.className = "song";

                const name = document.createElement("span");
                name.className = "song-name";
                name.textContent = file.name;

                const link = document.createElement("a");
                link.className = "download-button";
                link.textContent = "Download";
                link.href = `${API_URL}${file.url}`;

                row.appendChild(name);
                row.appendChild(link);

                results.appendChild(row);
            }
        }

    } catch (error) {

        status.textContent = "Something went wrong.";

        results.innerHTML = `
            <p class="error">
                ${escapeHtml(error.message)}
            </p>
        `;

    } finally {

        button.disabled = false;
        loading.classList.add("hidden");
    }
}


function escapeHtml(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}
