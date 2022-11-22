#pragma once

// Standard library
#include "clang/Basic/Diagnostic.h"
#include <string>
// Exteral
#include <nlohmann/json.hpp>
using json = nlohmann::ordered_json;

namespace QED { namespace Pragmatic {

	struct Meta
	{
		private:
		Meta() = default;
		public:
		static Meta& GetInstance(clang::Preprocessor& preprocessor);
		Meta(Meta const&) = delete;
        void operator=(Meta const&) = delete;
		~Meta() = default;

		public:
		std::string metaFilePath;
		json json;

		public:
		void ClearDefinitionsForFile(std::string file);
		void Write();
	};

}} // namesapce QED::Pragmatic