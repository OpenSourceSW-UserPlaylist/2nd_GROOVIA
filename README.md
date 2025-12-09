# 🎧 Groovia – Audio-based Music Recommendation Service

iTunes API에서 미리듣기 음원을 받아 Librosa로 오디오 특징을 분석하고,  
해당 특징 벡터 기반으로 가장 유사한 음악을 추천하는 **오디오 기반 음악 추천 서비스**입니다.

텍스트 기반 메타데이터만 활용하던 기존 방식(Ver.1)의 한계를 해결하고,  
**실제 음향 분석 기반의 정교한 추천(Ver.2)** 을 제공합니다.

---

## 목차
- [프로젝트 개요](#프로젝트-개요)
- [사용자 가이드](#사용자-가이드)
- [개발자 가이드](#개발자-가이드)
- [시스템 구조](#시스템-구조)
- [추천 알고리즘](#추천-알고리즘)
- [오디오 분석 방식](#오디오-분석-방식)
- [API 명세](#api-명세)
- [테스트 및 검증](#테스트-및-검증)
- [참고 자료](#참고-자료)

---

## 프로젝트 개요

Groovia는 사용자가 입력한 **곡명 + 아티스트명**을 기반으로  
iTunes Search API에서 30초 미리듣기 음원을 가져오고,  
Librosa로 **BPM, MFCC, Chroma** 등 오디오 특징을 추출해  
감성 분류 및 유사도 기반 추천을 수행하는 음악 추천 서비스입니다.

### Ver.1 → Ver.2 개선점
- **Spotify → iTunes 전환**, 안정적인 previewUrl 확보  
- 텍스트 기반 추천에서 **오디오 실제 특징 기반 추천**으로 고도화  
- BPM/음색/화음 기반의 정밀한 음악 추천 제공  

---

## 사용자 가이드

### 🎵 1. 곡 입력
사용자는 다음과 같은 형식으로 입력합니다:

```
IVE, Love Dive  
Jungkook, Seven
```

“추천 받기” 버튼 클릭 시 분석이 시작됩니다.

---

### 🧪 2. 분석 중 화면
- Django 백엔드가 iTunes API 호출  
- previewUrl 확보  
- Librosa로 오디오 분석(BPM, MFCC 등)  
- 감성 카테고리(4분면) 분류  
- 특징 기반 추천 리스트 생성  

로딩 화면이 표시됩니다.

---

### 📑 3. 결과 화면
- 추천 음악 리스트  
- 감성 카테고리(신나는/잔잔한/로맨틱 등)  
- BPM/무드 등 분석 정보  
- 다시 추천받기 기능  

---

### 📚 4. 라이브러리 화면
이전에 추천받은 곡들을 저장하고 확인할 수 있습니다.

---

## 개발자 가이드

### 🖥 Frontend (Flutter)
- Flutter 3.x  
- Dart  
- http, provider(or bloc), audioplayers 패키지 사용  

### 🔧 Backend (Django)
- Django 4.x  
- Django REST Framework  
- Librosa / numpy / scipy  
- requests(iTunes 연동)  

---

## 시스템 구조

### 구성 요소
1. **Flutter Frontend** → 사용자 입력 & UI  
2. **Django Backend** → 오디오 분석 + 추천  
3. **iTunes API** → 미리듣기 음원 제공  
4. **Librosa 분석기** → BPM/MFCC/Chroma 추출  

### 데이터 흐름
사용자 입력 → Django 수신 → iTunes 검색 → 오디오 분석 → 추천 결과 반환 → Flutter 표시

---

## 추천 알고리즘

### 1. 감성 카테고리(4분면) 분류
- Calm  
- Excited  
- Romantic  
- Energetic  

### 2. 추천 로직
1. 동일 감성 카테고리 곡 후보군 필터링  
2. BPM / MFCC / Chroma / RMS 특징 벡터화  
3. **유사도 계산 (코사인 or 유클리드)**  
4. 상위 N개 추천곡 반환  

사용: **HNSW 기반 Approximate Nearest Neighbor Search**

---

## 오디오 분석 방식

Librosa로 다음 특징을 추출합니다:

| 특징 | 설명 |
|------|------|
| **Tempo(BPM)** | 곡의 속도 |
| **MFCC** | 음색의 핵심 특징 |
| **Chroma** | 화음/코드 구성 |
| **RMS** | 곡의 음압/다이내믹 |

이 벡터들은 추천 알고리즘의 입력으로 사용됩니다.

---

## API 명세

### 🎯 POST `/api/analyze/`

#### Request
```json
{
  "artist": "IVE",
  "title": "Love Dive"
}
```

#### Response
```json
{
  "category": "romantic",
  "tempo": 122,
  "recommended": [
    {
      "title": "After LIKE",
      "artist": "IVE",
      "preview": "..."
    }
  ]
}
```

---

## 테스트 및 검증

- Flutter ↔ Django 연결 정상 작동  
- iTunes API 호출 성공 (preview 안정적 제공)  
- BPM/MFCC/Chroma 특징 추출 정상 작동  
- 추천 알고리즘 정확도 Ver.2에서 크게 향상  
- Ver.1 대비 오디오 기반 분석의 만족도 증가  

---

## 참고 자료

- Librosa Documentation  
- Scikit-learn API Guide  
- Apple iTunes Search API  
- Django REST Framework Docs  
- Flutter 공식 문서  
