function countDown() {
  Array.from(document.getElementsByClassName("expires-number")).forEach(
    (el) => {
      let number = el.innerText;
      if (number == 0) {
        return;
      }
      number = number - 1;
      el.innerText = number;
    }
  );
  setTimeout(countDown, 1000);
}

countDown();
