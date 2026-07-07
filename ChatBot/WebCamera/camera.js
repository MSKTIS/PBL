const video = document.getElementById("video");

async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: "environment" },
            audio: false
        });

        video.srcObject = stream;
        const track = stream.getVideoTracks()[0];
        const capabilities = track.getCapabilities();
        if (capabilities.zoom) {
            await track.applyConstraints({ advanced: [{ zoom: 2.7 }] });
        }
        video.play();
    }
    catch (e) {
        console.error(e);
        alert("カメラを起動できません");
    }
}
startCamera();

// 撮影処理
const canvas = document.getElementById("canvas");

document
    .getElementById("captureBtn")
    .addEventListener("click", () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext("2d");

        // カメラ映像
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // ダウンロード
        canvas.toBlob(async (blob) => {
            // 保存先データ
            const form = new FormData();
            formData.append("user_id", "{{ user_id }}");
            // 
            const res = await fetch("/upload", { method: "POST", body: form });
            if (res.ok) {
                alert("保存しました");
            }
        }, "image/png");
    });
const captureBtn = document.getElementById("captureBtn");