## User Guide
1. 곡 정보 입력: 사용자가 선호하는 곡의 곡명과 아티스트명을 입력
2. 음원 분석 요청: Django 백엔드로 곡 정보 전송, iTunnes API를 통해 30초 미리듣기 확보
3. 음원 특징 추출: Librosa 라이브러리를 통해 BPM, MFCC, Chroma 등의 음원 특징 추출, 감성 분류
4. 추천 플레이스트 생성: 유사한 분위기와 특성을 가진 곡들을 데이터베이스에서 찾아 플레이리스트 생성
5. 플레이스트 확인: Flutter 프론트엔드를 통해 시각적으로 제공

## Developer Guide
1. 전체 아키텍처 구성: Flutter 기반 프론트엔드와 Django 기반 백엔드로 구성
2. 입력 데이터 처리: Flutter에서 곡명과 아티스트명을 입력받아 Django 서버로 POST 요청 전송
3. 외부 API 연동: Django 백엔드는 iTunes API를 통해 입력받은 곡의 30초 미리듣기 음원(previewUrl) 가져옴
4. 음원 분석 로직 구현: Librosa 라이브러리를 활용하여 BPM, MFCC, Chroma, Spectral Centroid 등의 음원 특징을 추출
5. 유사 곡 추천 알고리즘 적용: 추출된 특징값을 기반으로 유사도 계산을 수행하여 가장 유사한 10곡을 추천
6. 추천 결과 데이터 처리: 추천된 10곡의 곡명, 가수명, 앨범 커버 정보를 CSV 형식으로 저장하고 Django에서 관리
9. 프론트엔드 전달 및 UI 출력: Django에서 추천 결과를 JSON 형태로 Flutter에 전달하며, Flutter는 이를 리스트 UI로 시각화하여 출력
