# Portfolio-of-Stocks
webアプリケーション上で株価の売買及びその管理が出来るアプリケーションを作成した．  
企業の株価はAPIを利用することで各企業の株価を取得し，所望の株式を購入・売却が可能．  
API : IEXより取得 (https://exchange.iex.io/products/market-data-connectivity/)  

## 使用技術  
・Python  
・SQL  
・html, CSS  
・Flask  

試運転の際は下記のコマンドを実行しFlaskを起動した後，以下の項目をご利用ください．  
$ export API_KEY=pk_bf978c58267c473181bac9b8568e9a31  

### URL  (ログイン画面)
https://ide-dddc674df4624f569f4ce2405f24ba7a-8080.cs50.ws/login

↓ログイン画面用  
ID : Kaname  
pass : Kaname8206  
  
### Main画面　（ログイン後のページ）  
https://ide-dddc674df4624f569f4ce2405f24ba7a-8080.cs50.ws/



## 全体の構成  
BootStrapを用いてレイアウトを作成．  
ログイン後のすべてのページに各ページへのリンクボタンを付与することで快適にページ遷移が行えるようにした．  
このアプリケーション上では主にポートフォリオの確認，株価の確認，株式の購入，株式の売却，株式取引履歴の確認，キャッシュの入金が行える．


## Register画面
ユーザーの新規登録が可能．IDとパスワードを入力することでデータベースにアカウントを登録できる．  
パスワードは誤登録を防ぐために二重に入力を促し，不備が無ければ登録可能．  
すでに登録済みのIDを入力した場合にはエラー画面に遷移し，その旨を伝える仕様にした．

-Register-
![register](https://user-images.githubusercontent.com/77096897/151731857-47053610-17db-4c86-b6fb-e63ba1638a54.png)


## Login画面  
予め登録されたユーザーIDとパスワードを入力することでログインできる．入力された情報がデータベース上にない場合はその旨をエラー画面と共に表示する．  
未登録の場合はregister画面にすぐに移れるように右上にボタンリンクを挿入した．  

-Log In-  
![login](https://user-images.githubusercontent.com/77096897/151732126-e7f4f2d7-334c-4728-83c4-5961bd1f31ed.png)


## Main画面  
所有している株式のポートフォリオを表示する．その株式の企業名，株価，持ち株数，株価を一覧で表示．一目で確認できる仕様にした．  
また，株式と共にキャッシュの残高も表示し，株式との合計の資産を確認できる．  
ページ上部には各ページへのボタンリンクを配置し押下することで各ページに遷移することが出来る．  
「Portfolio of Stocks」を押下することでメインページに，「Logout」を押下することでログアウトし，ログインページに遷移できる．  

-Main-  
![main](https://user-images.githubusercontent.com/77096897/151733138-fb3c45bd-122e-4555-a01a-0fdfa82b4822.png)


## Quote画面  
購入したい企業の略記号を入力することで現在の株式を確認することが出来る．  
取得したAPIデータから入力した企業の株価を抽出し画面に表示している．  

-Quote-  
![quote](https://user-images.githubusercontent.com/77096897/151733845-861a6732-0c0b-49ef-9216-e5d09038fd5c.png)


## Buy画面  
購入したい株式の種類と，株数を入力することで株式の購入が可能．  
手持ちのキャッシュの量と比べて株式の購入総額が大きい場合はエラー画面に遷移し，その旨を通知．  
購入した株式データは即時データベース上に反映され，Main画面上のポートフォリオにも持ち株の詳細や所有キャッシュの残高などが更新される．  

-Buy-  
![buy](https://user-images.githubusercontent.com/77096897/151734161-569b516e-06a7-4c83-a67a-2f6a1aed3d8f.png)  


## Sell画面  
手持ちの株式を売却できる．  
株式の種類を入力する部分にはドロップダウンを施し，持ち株の中からのみ選べるような仕様にした．  
株数を入力する部分に持ち株の数より多くの数字を記入した場合にはエラー画面と共にその旨を通知する．  
Buy画面と同様に更新されたデータはデータベースに反映され即時，Main画面上のポートフォリオに反映される．  

-Sell-  
![sell](https://user-images.githubusercontent.com/77096897/151734374-af924106-b1d2-479b-bbe1-7bffc1e358ca.png)  


## History画面  
株式の売買履歴を参照することが出来る．  
株式の購入と売却のログを記録し一覧で表示する仕様にした．株式の種類と取引価格，取引成立日時を表示．  

-Histroy-  
![history](https://user-images.githubusercontent.com/77096897/151734926-4b4a7aeb-3f50-45c3-b9b6-62330e414c5f.png)  


## Payment画面  
キャッシュの入金が行える．所望の入金額を入力することでデータベース上のキャッシュ残高を更新できる．  
更新したデータはMain画面上のポートフォリオにおいても即時反映される．  

-Payment-  
![payment](https://user-images.githubusercontent.com/77096897/151735095-a7eb13ba-0267-4310-8221-6fe57e11841d.png)
