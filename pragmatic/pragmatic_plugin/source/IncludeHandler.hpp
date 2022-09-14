// Pragmatic plugin
#include "PreamblePragmaHandler.hpp"

using namespace clang;

namespace QED { namespace Pragmatic
{
	class IncludeCallbacks : public Callbacks
	{
		public:
		IncludeCallbacks(clang::Preprocessor& pp) : Callbacks(pp) { }

		virtual void InclusionDirective
		(
			clang::SourceLocation HashLoc,
			const clang::Token &IncludeTok,
			clang::StringRef FileName,
			bool IsAngled,
			clang::CharSourceRange FilenameRange,
			clang::Optional<clang::FileEntryRef> File,
			clang::StringRef SearchPath,
			clang::StringRef RelativePath,
			const clang::Module *Imported,
			clang::SrcMgr::CharacteristicKind FileType
		) override;
	};
}} // namespace QED::Pragmatic