words = open('Словарь.txt', encoding="utf8").read().split()
answer, vocab = [], {}
for word in words:
    sorted_word = ''.join(sorted(word))
    if sorted_word in vocab:
        vocab[sorted_word].append(word)
    else:
        vocab[sorted_word] = [word]
print(', '.join(sorted(max(vocab.items(), key=lambda x: len(x[1]))[1])))
